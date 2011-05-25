/*

  This file is part of OpenMalaria.
 
  Copyright (C) 2005,2006,2007,2008 Swiss Tropical Institute and Liverpool School Of Tropical Medicine
 
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
#include "Host/Human.h"

#include "Host/InfectionIncidenceModel.h"
#include "Clinical/ClinicalModel.h"
#include "WithinHost/DescriptiveIPTWithinHost.h"        // only for summarizing

#include "inputData.h"
#include "Transmission/TransmissionModel.h"
#include "Monitoring/Surveys.h"
#include "PopulationStats.h"
#include "util/ModelOptions.h"
#include "util/random.h"
#include "util/StreamValidator.h"
#include "Interventions.h"

#include <string>
#include <string.h>
#include <cmath>
#include <algorithm>
#include <stdexcept>
#include <gsl/gsl_cdf.h>

namespace OM { namespace Host {
    using namespace OM::util;
    int Human::_ylagLen = 0;
    bool Human::cohortFirstBoutOnly = false;
    bool Human::cohortFirstTreatmentOnly = false;
    bool Human::cohortFirstInfectionOnly = false;

// -----  Static functions  -----

void Human::initHumanParameters () {    // static
    // Init models used by humans:
    Transmission::PerHostTransmission::init();
    InfectionIncidenceModel::init();
    WithinHost::WithinHostModel::init();
    Clinical::ClinicalModel::init();
    _ylagLen = TimeStep::intervalsPer5Days.asInt() * 4;
    
    cohortFirstBoutOnly = InputData().getMonitoring().getFirstBoutOnly();
    cohortFirstTreatmentOnly = InputData().getMonitoring().getFirstTreatmentOnly();
    cohortFirstInfectionOnly = InputData().getMonitoring().getFirstInfectionOnly();
}

void Human::clear() {   // static clear
  Clinical::ClinicalModel::cleanup();
  Transmission::PerHostTransmission::cleanup();
}


// -----  Non-static functions: creation/destruction, checkpointing  -----

// Create new human
Human::Human(Transmission::TransmissionModel& tm, TimeStep dateOfBirth) :
    perHostTransmission(),
    withinHostModel(WithinHost::WithinHostModel::createWithinHostModel()),
    infIncidence(InfectionIncidenceModel::createModel()),
    _dateOfBirth(dateOfBirth),
    nextCtsDist(0),
    _inCohort(false),
    _probTransmissionToMosquito(0.0)
{
  if (_dateOfBirth != TimeStep::simulation && (TimeStep::simulation > TimeStep(0) || _dateOfBirth > TimeStep::simulation))
    throw out_of_range ("Invalid date of birth!");
  
  _ylag.assign (_ylagLen, 0.0);
  
  
  /* Human heterogeneity; affects:
   * _comorbidityFactor (stored in PathogenesisModel)
   * _treatmentSeekingFactor (stored in CaseManagementModel)
   * availabilityFactor (stored in Transmission::PerHostTransmission)
   */
  double _comorbidityFactor = 1.0;
  double _treatmentSeekingFactor = 1.0;
  double availabilityFactor = 1.0;
  
  if (util::ModelOptions::option (util::TRANS_HET)) {
    availabilityFactor=0.2;
    if (random::uniform_01() < 0.5) {
      availabilityFactor=1.8;
    }
  }
  if (util::ModelOptions::option (util::COMORB_HET)) {
    _comorbidityFactor=0.2;
    if (random::uniform_01() < 0.5) {
      _comorbidityFactor=1.8;
    }   
  }
  if (util::ModelOptions::option (util::TREAT_HET)) {
    _treatmentSeekingFactor=0.2;
    if (random::uniform_01() < 0.5) {            
      _treatmentSeekingFactor=1.8;
    }   
  }
  if (util::ModelOptions::option (util::TRANS_TREAT_HET)) {
    _treatmentSeekingFactor=0.2;
    availabilityFactor=1.8;
    if (random::uniform_01()<0.5) {
      _treatmentSeekingFactor=1.8;
      availabilityFactor=0.2;
    }
  } else if (util::ModelOptions::option (util::COMORB_TREAT_HET)) {
    if (random::uniform_01()<0.5) {
      _comorbidityFactor=1.8;
      _treatmentSeekingFactor=0.2;
    } else {
      _comorbidityFactor=0.2;
      _treatmentSeekingFactor=1.8;
    }
  } else if (util::ModelOptions::option (util::COMORB_TRANS_HET)) {
    availabilityFactor=1.8;
    _comorbidityFactor=1.8;
    if (random::uniform_01()<0.5) {
      availabilityFactor=0.2;
      _comorbidityFactor=0.2;
    }
  } else if (util::ModelOptions::option (util::TRIPLE_HET)) {
    availabilityFactor=1.8;
    _comorbidityFactor=1.8;
    _treatmentSeekingFactor=0.2;
    if (random::uniform_01()<0.5) {
      availabilityFactor=0.2;
      _comorbidityFactor=0.2;
      _treatmentSeekingFactor=1.8;
    }
  }
  perHostTransmission.initialise (tm, availabilityFactor * infIncidence->getAvailabilityFactor(1.0));
  clinicalModel = Clinical::ClinicalModel::createClinicalModel (_comorbidityFactor, _treatmentSeekingFactor);
}

void Human::destroy() {
  delete infIncidence;
  delete withinHostModel;
  delete clinicalModel;
}


// -----  Non-static functions: per-timestep update  -----

bool Human::update(Transmission::TransmissionModel* transmissionModel, bool doUpdate) {
#ifdef WITHOUT_BOINC
    PopulationStats::humanUpdateCalls++;
    if( doUpdate )
        PopulationStats::humanUpdates++;
#endif
    TimeStep ageTimeSteps = TimeStep::simulation-_dateOfBirth;
    if (clinicalModel->isDead(ageTimeSteps))
        return true;
    
    if (doUpdate){
        util::streamValidate( ageTimeSteps.asInt() );
        double ageYears = ageTimeSteps.inYears();
        monitoringAgeGroup.update( ageYears );
        
        updateInterventionStatus();
        updateInfection(transmissionModel, ageYears);
        clinicalModel->update (*this, ageYears, ageTimeSteps);
        clinicalModel->updateInfantDeaths (ageTimeSteps);
        _probTransmissionToMosquito = calcProbTransmissionToMosquito ();
    }
    return false;
}

void Human::addInfection(){
    withinHostModel->newInfection();
}

void Human::updateInfection(Transmission::TransmissionModel* transmissionModel, double ageYears){
    double EIR = transmissionModel->getEIR( perHostTransmission, ageYears, monitoringAgeGroup );
    int numInf = infIncidence->numNewInfections( *this, EIR );
    for (int i=1;i<=numInf; i++) {
        withinHostModel->newInfection();
    }
    
    // Cache total density for infectiousness calculations
    _ylag[TimeStep::simulation.asInt()%_ylagLen]=withinHostModel->getTotalDensity();
    
    withinHostModel->calculateDensities(ageYears, _vaccine.getBSVEfficacy());
}

void Human::updateInterventionStatus() {
    if (TimeStep::interventionPeriod >= TimeStep(0)) {
        TimeStep ageTimeSteps = TimeStep::simulation-_dateOfBirth;
        //HACK
        InterventionManager::getSingleton().deployCts(*this, ageTimeSteps, nextCtsDist);
    }
}


void Human::massVaccinate () {
    _vaccine.vaccinate();
    Monitoring::Surveys.getSurvey(_inCohort).reportMassVaccinations (ageGroup(), 1);
}
void Human::ctsVaccinate () {
    if ( _vaccine.doCtsVaccination( TimeStep::simulation - _dateOfBirth ) ){
        _vaccine.vaccinate();
        Monitoring::Surveys.getSurvey(_inCohort).reportEPIVaccinations (ageGroup(), 1);
    }
}

void Human::IPTiTreatment () {
  withinHostModel->IPTiTreatment (ageGroup(), _inCohort);
}
void Human::deployIptDose () {
    withinHostModel->deployIptDose( ageGroup(), _inCohort );
}

void Human::massDrugAdministration () {
    clinicalModel->massDrugAdministration (*this);
}

void Human::massITN (){
    perHostTransmission.setupITN ();
    Monitoring::Surveys.getSurvey(_inCohort).reportMassITNs( ageGroup(), 1 );
}
void Human::ctsITN (){
    perHostTransmission.setupITN ();
    Monitoring::Surveys.getSurvey(_inCohort).reportEPI_ITNs( ageGroup(), 1 );
}

void Human::massIRS () {
    perHostTransmission.setupIRS ();
    Monitoring::Surveys.getSurvey(_inCohort).reportMassIRS( ageGroup(), 1 );
}

void Human::massVA () {
    perHostTransmission.setupVA ();
    Monitoring::Surveys.getSurvey(_inCohort).reportMassVA( ageGroup(), 1 );
}

bool Human::hasVaccineProtection(TimeStep maxInterventionAge) const{
    return _vaccine.hasProtection(maxInterventionAge);
}
bool Human::hasIPTiProtection(TimeStep maxInterventionAge) const{
    return withinHostModel->hasIPTiProtection(maxInterventionAge);
}
bool Human::hasITNProtection(TimeStep maxInterventionAge) const{
    return perHostTransmission.hasITNProtection(maxInterventionAge);
}
bool Human::hasIRSProtection(TimeStep maxInterventionAge) const{
    return perHostTransmission.hasIRSProtection(maxInterventionAge);
}
bool Human::hasVAProtection(TimeStep maxInterventionAge) const{
    return perHostTransmission.hasVAProtection(maxInterventionAge);
}

double Human::getAgeInYears() const{
    return (TimeStep::simulation - _dateOfBirth).inYears();
}


void Human::summarize() {
    // 5-day only, compatibility option:
    if( util::ModelOptions::option( util::REPORT_ONLY_AT_RISK ) &&
        clinicalModel->recentTreatment() ){
        // This modifies the denominator to treat the 4*5 day intervals
        // after a bout as 'not at risk' to match the IPTi trials
        return;
    }
    
    Monitoring::Survey& survey( Monitoring::Surveys.getSurvey( _inCohort ) );
    Monitoring::AgeGroup ageGrp = ageGroup();
    survey.reportHosts (ageGrp, 1);
    bool patent = withinHostModel->summarize (survey, ageGrp);
    infIncidence->summarize (survey, ageGrp);
    clinicalModel->summarize (survey, ageGrp);
    
    if( cohortFirstInfectionOnly && patent ){
        removeFromCohort();
    }
}

void Human::addToCohort (){
    assert( !_inCohort );
    // Data accumulated between reports should be flushed. Currently all this
    // data remembers which survey it should go to or is reported immediately,
    // although episode reports still need to be flushed.
    flushReports();
    _inCohort = true;
    Monitoring::Surveys.current->reportAddedToCohort( ageGroup(), 1 );
}
void Human::removeFromCohort(){
    if( _inCohort ){
        // Data should be flushed as with addToCohort().
        flushReports();
        _inCohort = false;
        Monitoring::Surveys.current->reportRemovedFromCohort( ageGroup(), 1 );
    }
}


void Human::flushReports (){
    clinicalModel->flushReports();
}


double Human::calcProbTransmissionToMosquito() const {
  /* This model (often referred to as the gametocyte model) was designed for
  5-day timesteps. We use the same model (sampling 10, 15 and 20 days ago)
  for 1-day timesteps to avoid having to design and analyse a new model.
  Description: AJTMH pp.32-33 */
  TimeStep ageTimeSteps=TimeStep::simulation-_dateOfBirth;
  if (ageTimeSteps.inDays() <= 20 || TimeStep::simulation.inDays() <= 20)
    return 0.0;
  
  //Infectiousness parameters: see AJTMH p.33, tau=1/sigmag**2 
  static const double beta1=1.0;
  static const double beta2=0.46;
  static const double beta3=0.17;
  static const double tau= 0.066;
  static const double mu= -8.1;
  
  // Take weighted sum of total asexual blood stage density 10, 15 and 20 days before.
  // These values are one timestep more recent than that, however the calculated
  // value is not used until the next timestep when then ages would be correct.
  int firstIndex = TimeStep::simulation.asInt()-2*TimeStep::intervalsPer5Days.asInt()+1;
  double x = beta1 * _ylag[firstIndex % _ylagLen]
           + beta2 * _ylag[(firstIndex-TimeStep::intervalsPer5Days.asInt()) % _ylagLen]
           + beta3 * _ylag[(firstIndex-2*TimeStep::intervalsPer5Days.asInt()) % _ylagLen];
  if (x < 0.001)
    return 0.0;
  
  double zval=(log(x)+mu)/sqrt(1.0/tau);
  double pone = gsl_cdf_ugaussian_P(zval);
  double transmit=(pone*pone);
  //transmit has to be between 0 and 1
  transmit=std::max(transmit, 0.0);
  transmit=std::min(transmit, 1.0);
  
  //    Include here the effect of transmission-blocking vaccination
  double ret = transmit*(1.0-_vaccine.getTBVEfficacy());
  util::streamValidate( ret );
  return ret;
}

} }