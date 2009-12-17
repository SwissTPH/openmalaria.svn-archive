/* This file is part of OpenMalaria.
 * 
 * Copyright (C) 2005-2009 Swiss Tropical Institute and Liverpool School Of Tropical Medicine
 * 
 * OpenMalaria is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or (at
 * your option) any later version.
 * 
 * This program is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
 */

#include "Transmission/Vector/VectorTransmission.h"
#include "inputData.h"
#include "util/vectors.h"
#include "util/ModelOptions.hpp"

#include <fstream>

namespace OM { namespace Transmission {
    using namespace OM::util;

VectorTransmission::VectorTransmission (const scnXml::Vector vectorData)
{
  if (!util::ModelOptions::option (util::NEGATIVE_BINOMIAL_MASS_ACTION)
      && !util::ModelOptions::option(util::LOGNORMAL_MASS_ACTION))
    throw util::xml_scenario_error ("VectorTransmission is incompatible with the original InfectionIncidenceModel");
  
  for (size_t j=0;j<Global::intervalsPerYear; j++)
    initialisationEIR[j]=0.0;
  
  // Each item in the AnophelesSequence represents an anopheles species.
  // TransmissionModel::createTransmissionModel checks length of list >= 1.
  const scnXml::Vector::AnophelesSequence anophelesList = vectorData.getAnopheles();
  numSpecies = anophelesList.size();
  if (numSpecies < 1)
    throw util::xml_scenario_error ("Can't use Vector model without data for at least one anopheles species!");
#ifdef OMV_CSV_REPORTING
  species.resize (numSpecies, VectorAnopheles(csvReporting));
  csvReporting << "simulation time,";
#else
  species.resize (numSpecies, VectorAnopheles());
#endif
  
  for (size_t i = 0; i < numSpecies; ++i) {
    string name = species[i].initialise (anophelesList[i], i,
					 initialisationEIR);
    speciesIndex[name] = i;
    
#ifdef OMV_CSV_REPORTING
    csvReporting << "N_v0("<<i<<"),N_v("<<i<<"),O_v("<<i<<"),S_v("<<i<<"),";
#endif
  }
  
#ifdef OMV_CSV_REPORTING
  csvReporting << "input EIR,resultant EIR,human infectiousness,human availability" << endl;
#endif
  
  // We want the EIR to effectively be the sum of the EIR for each day in the interval
  for (size_t i = 0; i < initialisationEIR.size(); ++i) {
    initialisationEIR[i] *= Global::interval;
    
    // Calculate total annual EIR
    annualEIR += initialisationEIR[i];
  }
  
  
  // -----  Initialise interventions  -----
  const scnXml::Interventions::AnophelesSequence& intervSeq = InputData.getInterventions().getAnopheles();
  for (scnXml::Interventions::AnophelesSequence::const_iterator it = intervSeq.begin(); it != intervSeq.end(); ++it) {
    species[getSpeciesIndex(it->getMosquito())].setInterventionDescription (*it);
  }
  for (map<string,size_t>::const_iterator it = speciesIndex.begin(); it != speciesIndex.end(); ++it)
      species[it->second].checkInterventionDescriptions (it->first);
}
VectorTransmission::~VectorTransmission () {
  for (size_t i = 0; i < numSpecies; ++i)
    species[i].destroy();
}

void VectorTransmission::setupNv0 (const std::list<Host::Human>& population, int populationSize) {
  for (size_t i = 0; i < numSpecies; ++i) {
    species[i].setupNv0 (i, population, populationSize);
  }
}

int VectorTransmission::vectorInitIterate () {
  bool iterate = false;
  for (size_t i = 0; i < numSpecies; ++i)
    iterate |= species[i].vectorInitIterate ();
  if (iterate) {
    simulationMode = equilibriumMode;
    return Global::intervalsPerYear*2;	//TODO: how long?
  } else {
    simulationMode = dynamicEIR;
    return 0;
  }
}

void VectorTransmission::initMainSimulation() {
  // Check every time at end of init that, to a low tolerence,
  // the average EIR produced is what was expected:
  if (!vectors::approxEqual(initialisationEIR, innoculationsPerDayOfYear)) {
    cerr << "Generated EIR not as expected (expected, generated):\n";
    cerr << initialisationEIR << '\n' << innoculationsPerDayOfYear << endl;
  }
  
  simulationMode = InputData.get_mode();	// allow forcing equilibrium mode like with non-vector model
  if (simulationMode != 2 && simulationMode != 4)
    throw util::xml_scenario_error("mode attribute has invalid value (expected: 2 or 4)");
}

double VectorTransmission::calculateEIR(int simulationTime, PerHostTransmission& host, double ageInYears) {
  if (simulationMode == equilibriumMode)
    return initialisationEIR[simulationTime%Global::intervalsPerYear]
	 * host.relativeAvailabilityHetAge (ageInYears) * PerHostTransmission::ageCorrectionFactor;
  
  double EIR = 0.0;
  for (size_t i = 0; i < numSpecies; ++i) {
    EIR += species[i].calculateEIR (i, host);
  }
  return EIR * PerHostTransmission::relativeAvailabilityAge (ageInYears) * PerHostTransmission::ageCorrectionFactor;
}


// Every Global::interval days:
void VectorTransmission::vectorUpdate (const std::list<Host::Human>& population, int simulationTime) {
#ifdef OMV_CSV_REPORTING
  csvReporting << simulationTime << ',';
#endif
  for (size_t i = 0; i < numSpecies; ++i)
    species[i].advancePeriod (population, simulationTime, i, simulationMode == dynamicEIR);
}

void VectorTransmission::intervLarviciding (const scnXml::Larviciding& anoph) {
  const scnXml::Larviciding::AnophelesSequence& seq = anoph.getAnopheles();
  for (scnXml::Larviciding::AnophelesSequence::const_iterator it = seq.begin(); it != seq.end(); ++it)
    species[getSpeciesIndex(it->getMosquito())].intervLarviciding(*it);
}


void VectorTransmission::checkpoint (istream& stream) {
    TransmissionModel::checkpoint (stream);
    species & stream;
}
void VectorTransmission::checkpoint (ostream& stream) {
    TransmissionModel::checkpoint (stream);
    species & stream;
}

} }