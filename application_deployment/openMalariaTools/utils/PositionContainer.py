#!/usr/bin/python
# -*- coding: utf-8 -*-

# This file is part of OpenMalaria.
# 
# Copyright (C) 2005-2010 Swiss Tropical Institute and Liverpool School Of Tropical Medicine
# 
# OpenMalaria is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or (at
# your option) any later version.
# 
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

import re

'''PositionContainer:
This class is used to sort positions in a treeview (using liststore).
Algorithms could be improved, but this seems good enough.
'''
class PositionContainer():
    def __init__(self, reverse_order):
        self.positions_names = list()
        self.positions_numbers = list()
        self.reverse_order = reverse_order
    
    '''
    add:
    Adds a position in the list, the position name is compared with the others and alphabetically ordered'''
    def add(self, position_name, actual_position):
        
        position_name = self.search_int_value(position_name)
        
        if len(self.positions_names) > 0:
            if not self.reverse_order:
                i = 0
                while(i < len(self.positions_names) and cmp(self.positions_names[i], position_name)>=0):
                    i+=1
            else:
                i = 0
                while(i < len(self.positions_names) and cmp(self.positions_names[i], position_name)<=0):
                    i+=1
                
            if i == len(self.positions_names):
                self.positions_names.append(position_name)
                self.positions_numbers.append(actual_position)
            else:
                self.positions_names.insert(i, position_name)
                self.positions_numbers.insert(i, actual_position) 
        else:
            self.positions_names.append(position_name)
            self.positions_numbers.append(actual_position)
            
    '''
    test_for_int:
    Tries to transform the current string to an int
    '''
    def test_for_int(self, value):
        try:
            return int(value)
        except:
            return value
    '''
    search_int_value:
    Seaches for int values in a string and then returns a map back.
    This function is useful for comparing names like scenario_11 and scenario_2.
    '''    
    def search_int_value(self, value):
        return map(self.test_for_int, re.findall(r'(\d+|\D+)',value))
    
    '''
    get_positions_numbers:
    Returns the a list of number corresponding to the positions' actual indexes
    in the liststore.
    '''
    def get_positions_numbers(self):
        return self.positions_numbers