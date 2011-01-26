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

#include "Host/Vaccine.h"
#include "inputData.h"
#include "util/random.h"
#include "util/errors.h"

#include <cmath>

namespace OM {
namespace Host {
using namespace OM::util;

vector<TimeStep> Vaccine::targetAgeTStep;
size_t Vaccine::_numberOfEpiDoses = 0;
Vaccine Vaccine::PEV;
Vaccine Vaccine::BSV;
Vaccine Vaccine::TBV;


double Vaccine::getEfficacy (int numPrevDoses)
{
    /* If initialMeanEfficacy.size or more doses have already been given, use
     * the last efficacy. */
    if (numPrevDoses >= (int) initialMeanEfficacy.size())
        numPrevDoses = initialMeanEfficacy.size() - 1;
    double ime = initialMeanEfficacy[numPrevDoses];
    if (ime < 1.0) {
        double a = efficacyB * ime / ( 1.0 - ime );
        return random::beta (a, efficacyB);
    } else
        return 1.0;
}

void Vaccine::init()
{
    const scnXml::VaccineDescription *VdPEV = 0, *VdBSV = 0, *VdTBV = 0;
    const scnXml::Interventions& interventions = InputData().getInterventions();
    const scnXml::Descriptions::VaccineDescriptionSequence& vaccDesc =
	interventions.getDescriptions().getVaccineDescription();
    if (vaccDesc.size() == 0) {
        if (InputData.getActiveInterventions()[Interventions::VACCINE])
            throw util::xml_scenario_error ("Vaccine intervention without description");
	// Note: R_0 intervention uses vaccines, but not deployment; hence
	// it is safe to use without vaccine descriptions.
        return;
    }
    for (scnXml::Descriptions::VaccineDescriptionConstIterator i = vaccDesc.begin();
            i != vaccDesc.end(); i++) {
        const string& type = i->getVaccineType();
        if (type == "PEV")
            VdPEV = & (*i);
        else if (type == "BSV")
            VdBSV = & (*i);
        else if (type == "TBV")
            VdTBV = & (*i);
        else
            throw util::xml_scenario_error ("vaccineType invalid");
    }

    //Read in vaccine specifications
    PEV.initVaccine (VdPEV);
    BSV.initVaccine (VdBSV);
    TBV.initVaccine (VdTBV);

    if (interventions.getContinuous().present())
        _numberOfEpiDoses = interventions.getContinuous().get().getVaccine().size();
    if (_numberOfEpiDoses) {
        targetAgeTStep.resize (_numberOfEpiDoses, TimeStep(0));
        const scnXml::Continuous::VaccineSequence& cVS = interventions.getContinuous().get().getVaccine();
        for (size_t i = 0;i < _numberOfEpiDoses; i++) {
            if (i >= cVS.size()) {
                ostringstream msg;
                msg << "Expected " << _numberOfEpiDoses << " vaccine parameters in scenario.xml: interventions->continuous";
                throw util::xml_scenario_error (msg.str());
            }
            targetAgeTStep[i] = TimeStep::fromYears( cVS[i].getTargetAgeYrs() );
        }
    }
}

void Vaccine::initVaccine (const scnXml::VaccineDescription* vd)
{
    if (vd != NULL) {
        active = true;

        // set efficacyB:
        efficacyB = vd->getEfficacyB().getValue();

        // set initialMeanEfficacy:
        const scnXml::VaccineDescription::InitialEfficacySequence ies = vd->getInitialEfficacy();
        initialMeanEfficacy.resize (ies.size());
        for (size_t i = 0; i < initialMeanEfficacy.size(); ++i)
            initialMeanEfficacy[i] = ies[i].getValue();

        decayFunc = DecayFunction::makeObject( vd->getDecay(), "decay" );
    }
}

void Vaccine::cleanup ()
{
}


PerHumanVaccine::PerHumanVaccine() :
        _lastVaccineDose(0), _timeLastVaccine(TimeStep::never),
        _initialBSVEfficacy(0.0), _initialPEVEfficacy(0.0), _initialTBVEfficacy(0.0)
{
}

void PerHumanVaccine::vaccinate() {
    //Index to look up initial efficacy relevant for this dose.
    if (Vaccine::PEV.active)
        _initialPEVEfficacy = Vaccine::PEV.getEfficacy(_lastVaccineDose);

    if (Vaccine::BSV.active)
        _initialBSVEfficacy = Vaccine::BSV.getEfficacy(_lastVaccineDose);

    if (Vaccine::TBV.active)
        _initialTBVEfficacy = Vaccine::TBV.getEfficacy(_lastVaccineDose);

    ++_lastVaccineDose;
    _timeLastVaccine = TimeStep::simulation;
}
bool PerHumanVaccine::hasProtection(TimeStep maxInterventionAge)const{
    return _timeLastVaccine + maxInterventionAge > TimeStep::simulation;
}

}
}