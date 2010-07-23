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

#include "util/errors.hpp"

/** Standard exception classes for OpenMalaria. */
namespace OM { namespace util {
    
xml_scenario_error::xml_scenario_error(const string&  __arg)
  : runtime_error(__arg) { }

checkpoint_error::checkpoint_error(const string&  __arg)
  : runtime_error(__arg) { }

cmd_exit::cmd_exit(const string& __arg)
  : runtime_error(__arg) { }
   
} }