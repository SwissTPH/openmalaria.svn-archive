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

#ifndef Hmod_Simulation
#define Hmod_Simulation

#include "Global.h"
#include "population.h"

using namespace std;

namespace OM {
    
//! Main simulation class
class Simulation{
public: 
  //!  Inititalise all step specific constants and variables.
  Simulation();
  ~Simulation();

  //! Entry point to simulation.
  int start();

  //!  This procedure starts with the current state of the simulation 
  /*! It continues updating    assuming:
    (i)		the default (exponential) demographic model
    (ii)	the entomological input defined by the EIRs in intEIR()
    (iii)	the intervention packages defined in Intervention()
    (iv)	the survey times defined in Survey() */
  void mainSimulation();
  
  /// Initialisation phase for Vector model
  void vectorInitialisation();
  
  /*! Run the simulation using the equilibrium inoculation rates over one complete
    lifespan (maxAgeIntervals) to reach immunological equilibrium in all age
    classes. Don't report any events */
  void updateOneLifespan();

private:
  /** @brief checkpointing functions
   *
   * readCheckpoint/writeCheckpoint prepare to read/write the file,
   * and read/write read and write the actual data. */
  //@{
  //! This function reads the checkpoint from the file in which is written
  /*! if it exists and initializes all the data return true if the workunit is
  checkpointed and false otherwise */
  bool isCheckpoint();
  
  void writeCheckpoint();
  void readCheckpoint();
  
  void checkpoint (istream& stream);
  void checkpoint (ostream& stream);
  //@}
  
private:
  int simPeriodEnd;
  int totalSimDuration;
  
  Population* _population;

  friend class VectorAnophelesSuite;
};

}
#endif
