/*
 This file is part of OpenMalaria.
 
 Copyright (C) 2005-2009 Swiss Tropical Institute and Liverpool School Of Tropical Medicine
 
 OpenMalaria is free software; you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation; either version 2 of the License, or (at
 your option) any later version.
 
 This program is distributed in the hope that it will be useful, but
 WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 General Public License for more details.
 
 You should have received a copy of the GNU General Public License
 along with this program; if not, write to the Free Software
 Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
*/
#include "Transmission/NonVector.h"
#include "Transmission/PerHostTransmission.h"
#include "inputData.h"
#include "util/random.h"
#include "util/vectors.h"
#include "Monitoring/Surveys.h"	// sim-end timestep
#include <limits>

namespace OM { namespace Transmission {
    namespace vectors = util::vectors;

//static (class) variables
const double NonVectorTransmission::totalInfectionrateVariance= 1.0;
const double NonVectorTransmission::min_EIR_mult= 0.01; 

NonVectorTransmission::NonVectorTransmission(const scnXml::NonVector& nonVectorData)
{
  nspore = nonVectorData.getEipDuration() / Global::interval;
  
  initialKappa.resize (Global::intervalsPerYear);
  
  vector<int> nDays (Global::intervalsPerYear, 0);
  //The minimum EIR allowed in the array. The product of the average EIR and a constant.
  double minEIR=min_EIR_mult*averageEIR(nonVectorData);
  const scnXml::NonVector::EIRDailySequence& daily = nonVectorData.getEIRDaily();
  if( daily.size() < static_cast<size_t>(Global::DAYS_IN_YEAR) )
      throw util::xml_scenario_error( "insufficient EIRDaily data for a year" );
  for (size_t mpcday = 0; mpcday < daily.size(); ++mpcday) {
    double EIRdaily = std::max((double)daily[mpcday], minEIR);
    
    // istep is the time period to which the day is assigned.  The result of the
    // division is automatically rounded down to the next integer.
    size_t i1 = (mpcday / Global::interval) % Global::intervalsPerYear;
    //EIR() is the sum of the EIRs assigned to the 73 different recurring time points
    nDays[i1]++;
    initialisationEIR[i1] += EIRdaily;
  }
  
  // Calculate total annual EIR
  // divide by number of records assigned to each interval (usually one per day)
  for (size_t j=0;j<Global::intervalsPerYear; j++) {
    initialisationEIR[j] *= Global::interval / (double)nDays[j];
    annualEIR += initialisationEIR[j];
  }
}

NonVectorTransmission::~NonVectorTransmission () {}

void NonVectorTransmission::scaleEIR (double factor){
    vectors::scale( initialisationEIR, factor );
    annualEIR = vectors::sum( initialisationEIR );
}
void NonVectorTransmission::scaleXML_EIR (scnXml::EntoData& ed, double factor) const{
    assert( ed.getNonVector().present() );
    scnXml::NonVector::EIRDailySequence& daily = ed.getNonVector().get().getEIRDaily();
    
    for( scnXml::NonVector::EIRDailyIterator it = daily.begin();
	it != daily.end(); ++it ){
	double old = *it;
	*it = old * factor;
    }
}


//! initialise the main simulation 
void NonVectorTransmission::initMainSimulation (){
  // initialKappa is used in calculateEIR
  initialKappa = kappa;
  // error check:
  for (size_t  i = 0; i < initialKappa.size(); ++i) {
      if (!(initialKappa[i] > 0.0))	// if not positive
	  throw runtime_error ("initialKappa is invalid");
  }
  
  simulationMode = InputData().getEntoData().getMode();
  if (simulationMode != 2 && simulationMode != 4)
      // Note: previously 3 was allowed -- but mode is set to 3 anyway when
      // "intervention" EIR data is loaded, so 2 or 4 should be used here.
      throw util::xml_scenario_error("mode attribute has invalid value (expected: 2 or 4)");
}

int NonVectorTransmission::transmissionInitDuration (){
    // 0 maintains old behaviour; human infectiousness over the last year of
    // human initialisation is used.
    return 0;
}

void NonVectorTransmission::setTransientEIR (const scnXml::NonVector& nonVectorData) {
    // Note: requires Global::timeStep >= 0, but this can only be called in intervention period anyway.
  simulationMode = transientEIRknown;
  
  if (nspore != nonVectorData.getEipDuration() / Global::interval)
      throw util::xml_scenario_error ("change-of-EIR intervention cannot change EIP duration");
  
  const scnXml::NonVector::EIRDailySequence& daily = nonVectorData.getEIRDaily();
  vector<int> nDays ((daily.size()-1)/Global::interval + 1, 0);
  interventionEIR.assign (nDays.size(), 0.0);
  if (static_cast<int>(nDays.size()) < Monitoring::Surveys.getFinalTimestep()+1) {
    cerr << "Days: " << daily.size() << "\nIntervals: " << nDays.size() << "\nRequired: " << Monitoring::Surveys.getFinalTimestep()+1 << endl;
    throw util::xml_scenario_error ("Insufficient intervention phase EIR values provided");
  }
  //The minimum EIR allowed in the array. The product of the average EIR and a constant.
  double minEIR=min_EIR_mult*averageEIR(nonVectorData);
  for (size_t mpcday = 0; mpcday < daily.size(); ++mpcday) {
    double EIRdaily = std::max((double)daily[mpcday], minEIR);
    
    // istep is the time period to which the day is assigned.  The result of the
    // division is automatically rounded down to the next integer.
    size_t istep = mpcday / Global::interval;
    nDays[istep]++;
    interventionEIR[istep] += EIRdaily;
  }
  // divide by number of records assigned to each interval (usually one per day)
  for (size_t i = 0; i < interventionEIR.size(); ++i)
    interventionEIR[i] *= Global::interval / nDays[i];
  
  // I've no idea what this should be, so until someone asks it can be NaN.
  // It was -9.99 and later 0.0. It could of course be recalculated from interventionEIR.
  annualEIR = numeric_limits<double>::quiet_NaN();
}

void NonVectorTransmission::changeEIRIntervention (const scnXml::NonVector& ed) {
    setTransientEIR (ed);
}

void NonVectorTransmission::uninfectVectors(){
    if( simulationMode != dynamicEIR )
	cerr <<"Warning: uninfectVectors is not effectaceous with changeEIR"<<endl;
    kappa.assign( kappa.size(), 0.0 );	// reset history of human infectivity, which scales dynamic EIR
}


double NonVectorTransmission::calculateEIR(int simulationTime, PerHostTransmission& perHost, const AgeGroupData ageGroupData){
  // where the full model, with estimates of human mosquito transmission is in use, use this:
  double eir;
  switch (simulationMode) {
    case equilibriumMode:
      eir = initialisationEIR[(simulationTime-1) % Global::intervalsPerYear];
      break;
    case transientEIRknown:
      // where the EIR for the intervention phase is known, obtain this from
      // the interventionEIR array
      eir = interventionEIR[Global::timeStep];
      break;
    case dynamicEIR:
      eir = initialisationEIR[(simulationTime-1) % Global::intervalsPerYear];
      if (Global::timeStep >= 0) {
	  // we modulate the initialization based on the human infectiousness nspore timesteps ago in the
	  // simulation relative to infectiousness at the same time-of-year, pre-intervention.
	  // nspore gives the sporozoite development delay.
	eir *=
            kappa[(simulationTime-nspore-1) % Global::intervalsPerYear] /
            initialKappa[(simulationTime-nspore-1) % Global::intervalsPerYear];
      }
      break;
    default:	// Anything else.. don't continue silently
      throw util::xml_scenario_error ("Invalid simulation mode");
  }
#ifndef NDEBUG
  if (!finite(eir)) {
    ostringstream msg;
    msg << "Error: non-vect eir is: " << eir
	<< "\nkappa:\t" << kappa[(simulationTime-nspore-1) % Global::intervalsPerYear]
	<< "\ninitialKappa:\t" << initialKappa[(simulationTime-nspore-1) % Global::intervalsPerYear] << endl;
    throw overflow_error(msg.str());
  }
#endif
  return eir * perHost.relativeAvailabilityHetAge (ageGroupData);
}


// -----   Private functs ------

double NonVectorTransmission::averageEIR (const scnXml::NonVector& nonVectorData) {
  // Calculates the arithmetic mean of the whole daily EIR vector read from the .XML file
  double valaverageEIR=0.0;
  size_t i = 0;
  for (const scnXml::NonVector::EIRDailySequence& daily = nonVectorData.getEIRDaily();
       i < daily.size(); ++i) {
    valaverageEIR += (double)daily[i];
  }
  return valaverageEIR / i;
}


// -----  checkpointing  -----

void NonVectorTransmission::checkpoint (istream& stream) {
    TransmissionModel::checkpoint (stream);
    nspore & stream;
    interventionEIR & stream;
    initialKappa & stream;
}
void NonVectorTransmission::checkpoint (ostream& stream) {
    TransmissionModel::checkpoint (stream);
    nspore & stream;
    interventionEIR & stream;
    initialKappa & stream;
}

} }
