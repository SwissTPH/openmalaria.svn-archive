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

#include "util/gsl.h"
#include "WithinHost/Empirical.h"
#include "Simulation.h"
#include "inputData.h"

using namespace std;

// -----  Initialization  -----

EmpiricalWithinHostModel::EmpiricalWithinHostModel() :
    WithinHostModel(), drugProxy(DrugModel::createDrugModel ()),
    _MOI(0)
{
}
EmpiricalWithinHostModel::~EmpiricalWithinHostModel() {
  clearAllInfections();
  delete drugProxy;
}

EmpiricalWithinHostModel::EmpiricalWithinHostModel(istream& in) :
    WithinHostModel(in), drugProxy(DrugModel::createDrugModel (in))
{
  in >> _MOI; 
  
  if (_MOI < 0 || _MOI > MAX_INFECTIONS)
    throw checkpoint_error ("_MOI");
  
  for(int i=0;i<_MOI;++i)
    infections.push_back(EmpiricalInfection(in));
}
void EmpiricalWithinHostModel::write(ostream& out) const {
  WithinHostModel::write (out);
  drugProxy->write (out);
  
  out << _MOI << endl; 
  
  for(std::list<EmpiricalInfection>::const_iterator iter=infections.begin(); iter != infections.end(); iter++)
    iter->write (out);
}


// -----  Simple infection adders/removers  -----

void EmpiricalWithinHostModel::newInfection(){
  if (_MOI < MAX_INFECTIONS) {
    infections.push_back(EmpiricalInfection(Simulation::simulationTime, 1));
    _MOI++;
  }
}

void EmpiricalWithinHostModel::clearAllInfections(){
  infections.clear();
  _MOI=0;
}


// -----  medicate drugs -----

void EmpiricalWithinHostModel::medicate(string drugName, double qty, int time, double age) {
  drugProxy->medicate(drugName, qty, time, age, 120.0 * wtprop[getAgeGroup(age)]);
}


// -----  Density calculations  -----

void EmpiricalWithinHostModel::calculateDensities(double ageInYears, double BSVEfficacy) {
  totalDensity = 0.0;
  timeStepMaxDensity = 0.0;
  std::list<EmpiricalInfection>::iterator i;
  for(i=infections.begin(); i!=infections.end();){
    double survivalFactor = (1.0-BSVEfficacy);
    survivalFactor *= drugProxy->getDrugFactor(i->getProteome());
    survivalFactor *= i->immunitySurvivalFactor(ageInYears, _cumulativeh, _cumulativeY);
    //TODO: innate immunity (_innateImmunity in Descriptive)
    
    // We update the density, and if updateDensity returns true (parasites extinct) then remove the infection.
    if (i->updateDensity(Simulation::simulationTime, survivalFactor)) {
      i = infections.erase(i);	// i points to next infection now so don't increment with ++i
      --_MOI;
      continue;	// infection no longer exists so skip the rest
    }
    
    double dens = i->getDensity();
    totalDensity += dens;
    timeStepMaxDensity = max(timeStepMaxDensity, dens);
    ++i;
  }
  drugProxy->decayDrugs();
}


// -----  Summarize  -----

int EmpiricalWithinHostModel::countInfections (int& patentInfections) {
  if (infections.empty()) return 0;
  patentInfections = 0;
  for (std::list<EmpiricalInfection>::iterator iter=infections.begin();
       iter != infections.end(); ++iter){
    if (iter->getDensity() > detectionLimit)
      patentInfections++;
  }
  return infections.size();
}
