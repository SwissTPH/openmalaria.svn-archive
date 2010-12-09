/*
 This file is part of OpenMalaria.
 
 Copyright (C) 2005-2010 Swiss Tropical Institute and Liverpool School Of Tropical Medicine
 
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

#include "AgeGroupData.h"
#include "Global.h"
#include <limits>

const double AgeGroupData::bsa_prop[AgeGroupData::nages] = {0.1843, 0.2225, 0.252, 0.2706, 0.2873, 0.3068, 0.3215, 0.3389, 0.3527, 0.3677, 0.3866, 0.3987, 0.4126, 0.4235, 0.441, 0.4564, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5 };
double AgeGroupData::ageSpecificRelativeAvailability[AgeGroupData::nages];


// weight proportions, used by drug code
const double AgeGroupData::agemin[nages] = { 0.0, 0.99, 1.99, 2.99, 3.99, 4.99, 5.99, 6.99, 7.99, 8.99, 9.99, 10.99, 11.99, 12.99, 13.99, 14.99, 19.99, 24.99, 29.99, 39.99, 49.99, 59.99, numeric_limits<double>::infinity()};

void AgeGroupData::initParameters () {
    for (size_t i=0; i < AgeGroupData::nages; i++) {
	ageSpecificRelativeAvailability[i] = bsa_prop[i] / (1-bsa_prop[i]);
    }
}

void AgeGroupData::update (double ageYears) {
    while (ageYears > agemin[_i+1])
	_i++;
}
