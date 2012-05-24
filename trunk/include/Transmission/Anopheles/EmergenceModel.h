/* This file is part of OpenMalaria.
 *
 * Copyright (C) 2005-2012 Swiss Tropical Institute and Liverpool School Of Tropical Medicine
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

#ifndef Hmod_Anopheles_EmergenceModel
#define Hmod_Anopheles_EmergenceModel

#include "Global.h"
#include "schema/interventions.h"
#include <vector>

namespace OM {
namespace Transmission {
namespace Anopheles {

using namespace std;

// forward declare to avoid circular dependency:
class Transmission;

/** Part of vector anopheles model, giving emergence of adult mosquitoes from
 * water bodies.
 * 
 * This is an abstract class (i.e. interface). The following implementations
 * exist: FixedEmergence.
 */
class EmergenceModel
{
public:
    ///@brief Initialisation and destruction
    //@{
    EmergenceModel() {}
    virtual ~EmergenceModel() {}
    
    /** Called by initialise function to init variables directly related to EIR
     * 
     * @param anoph Data from XML
     * @param initialisationEIR In/out parameter: TransmissionModel::initialisationEIR
     * @param EIPDuration parameter from Transmission (used for an estimation)
     */
    virtual void initEIR(
        const scnXml::AnophelesParams& anoph,
        vector<double>& initialisationEIR,
        int EIPDuration ) =0;
    
    /** Scale the internal EIR representation by factor; used as part of
     * initialisation. */
    virtual void scaleEIR( double factor ) =0;
    
    /** Latter part of AnophelesModel::init2.
     *
     * @param tsP_A P_A for this time step.
     * @param tsP_df P_df for this time step.
     * @param EIRtoS_v multiplication factor to convert input EIR into required
     * @param transmission reference to Transmission object
     * S_v. */
    virtual void init2( double tsP_A, double tsP_df, double EIRtoS_v, Transmission& transmission ) =0;
    
    /** Work out whether another interation is needed for initialisation and if
     * so, make necessary changes.
     *
     * @returns true if another iteration is needed. */
    virtual bool initIterate (Transmission& transmission) =0;
    //@}
    
    /// Update per time-step (for larviciding intervention). Call before
    /// getting emergence each time-step.
    virtual void update () =0;
    
    /** Return the emergence for today, taking interventions like larviciding
     * into account.
     * 
     * @param dYear1 Index for day of year (between 0 and 364)
     */
    virtual double get( size_t dYear1 ) const =0;
    
    /** Called at the end of each day's update to give the model data it needs
     * during initialisation.
     * 
     * @param d Day counter of simulation
     * @param S_v Value of S_v for this day
     */
    virtual void updateStats( size_t d, double S_v ) =0;
    
    ///@brief Interventions and reporting
    //@{
    /// Start a larviciding intervention.
    virtual void intervLarviciding (const scnXml::LarvicidingDescAnoph&) =0;
    //@}
    
    /// Checkpointing
    template<class S>
    void operator& (S& stream) {
        checkpoint (stream);
    }
    
protected:
    virtual void checkpoint (istream& stream) =0;
    virtual void checkpoint (ostream& stream) =0;
};

}
}
}
#endif