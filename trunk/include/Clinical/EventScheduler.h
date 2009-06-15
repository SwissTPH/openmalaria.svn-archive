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

#ifndef Hmod_ClinicalEventSchduler
#define Hmod_ClinicalEventSchduler

#include "Clinical/ClinicalModel.h"
#include "NewCaseManagement.h"

class ClinicalEventScheduler : public ClinicalModel
{
public:
  static void init ();
  
  ClinicalEventScheduler (double cF, double tSF);
  ClinicalEventScheduler (istream& in);
  ~ClinicalEventScheduler ();
  
  void write (ostream& out);
  
  void doCaseManagement (WithinHostModel& withinHostModel, double ageYears);
  
  inline bool recentTreatment() {
    return caseManagement->recentTreatment();
  }
  
private:
  //TODO move implementation to derived class
  /// The CaseManagementModel decides how to treat ill individuals
  NewCaseManagement * caseManagement;
};
#endif
