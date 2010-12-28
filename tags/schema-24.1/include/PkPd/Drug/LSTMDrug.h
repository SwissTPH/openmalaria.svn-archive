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

#ifndef Hmod_LSTMDrug
#define Hmod_LSTMDrug

#include "Global.h"
#include "LSTMDrugType.h"

using namespace std;

namespace OM {

namespace PkPd {
    struct DoseParams;
}
namespace util { namespace checkpoint {
    void operator& (multimap<double,PkPd::DoseParams> x, ostream& stream);
    void operator& (multimap<double,PkPd::DoseParams>& x, istream& stream);
} }

namespace PkPd {

  /** Describes an oral or IV dose.
   * 
   * If duration > 0, describes an IV dose. qty refers to the infusion rate
   * in mg/kg/day.
   * 
   * If duration = 0, describes an oral dose. qty refers to the concentration
   * in mg/kg.
   */
  struct DoseParams {
      DoseParams() : qty(0.0), duration(0.0) {}
      DoseParams( double r, double d ): qty(r), duration(d) {}
      double qty;               // infusion rate or dose size
      //NOTE: duration is now only needed when checking for overlapping doses
      // and not within factor/concentration calculation code.
      double duration;  // units: days
  
        /// Checkpointing
        template<class S>
        void operator& (S& stream) {
            qty & stream;
            duration & stream;
        }
  };    
    
/** A class holding pkpd drug use info.
 *
 * Each human has an instance for each type of drug present in their blood. */					
class LSTMDrug {
public:
  /** Create a new instance. */
  LSTMDrug (const LSTMDrugType&);
  
  inline string getAbbreviation() const { return typeData->abbreviation;}
  
  /** Indicate a new medication this timestep.
   *
   * Converts qty in mg to concentration, and stores along with time (delay past
   * the start of the current timestep) in the doses container. */
  void medicate (double time, double qty, double weight);
  /** Indicate a new medication via IV this timestep.
   *
   * @param duration Days
   * @param endTime Time between start of current timestep and end-time of
   * the dose in days. May be greater than 1 day, but endTime-duration must be
   * less than 1.
   * @param qty Mg/kg
   */
  void medicateIV (double duration, double endTime, double qty);
  
  /** Returns the total drug factor for one drug over one day.
   *
   * The drug factor values generated by this function must be multiplied to
   * reflect the drug action of all drugs in one day.
   * 
   * This doesn't adjust concentration because this function may be called
   * several times (for each infection) per timestep, or not at all. */
  double calculateDrugFactor(uint32_t proteome_ID);
  
  /** Updates concentration variable and clears day's doses.
   *
   * @returns true if concentration is negligible (this class instance can be removed). */
  bool updateConcentration ();
  
  /// Checkpointing
  template<class S>
  void operator& (S& stream) {
      concentration & stream;
      doses & stream;
  }
  
protected:
  typedef multimap<double,DoseParams> DoseMap;
  
    /** Check whether an IV dose needs to be split into multiple doses
     * (over two days or when an oral dose occurs in the middle).
     * If necessary, split.
     *
     * Only check against lastInserted. */
    void check_split_IV( DoseMap::iterator lastInserted );
    
  /// Always links a drug instance to its drug-type data
  const LSTMDrugType* typeData;
  
  double concentration;
  
  /** List of each dose given today (and possibly tomorrow), ordered by time.
   * First parameter (key) is time in days, second describes dose.
   * 
   * Used in calculateDrugFactor temporarily,
   * and in updateConcentration() to update concentration. */
   DoseMap doses;
};

} }
#endif