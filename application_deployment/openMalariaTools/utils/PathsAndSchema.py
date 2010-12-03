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

import os
import string
import sys
import tempfile

'''
PathsAndSchema:
This class is used for setting important paths and the schema version.
Those informations can be accessed statically by the other classes.
Reminder: There is no private variables in python. The underscore is just there to remind us not to give access
directly to the variables, but only to the get_ methods.
'''
class PathsAndSchema():
    
    _base_path =  os.getcwd()
    _temp_path = _base_path
    _home_path = _base_path
    
    if not sys.platform == 'win32':
        _temp_path = tempfile.gettempdir()
        _home_path = os.getenv("HOME") 
    	_base_path = '/usr/local/openmalariaTools' 
        
    _application_folder = os.path.join(_base_path, 'application')
    _common_folder = os.path.join(_base_path, 'application', 'common')
    
    _schema_translator_path = os.path.join(_base_path, 'application', 'schemaTranslator', 'SchemaTranslator.jar')
    _experiment_creator_path = os.path.join(_base_path, 'application', 'experiment_creator', 'experiment_creator.jar')
    _livegraph_path = os.path.join(_base_path, 'application', 'LiveGraph.2.0.beta01.Complete', 'LiveGraph.2.0.beta01.Complete.jar')
    _settings_file_path = os.path.join(_base_path, 'application', 'common', 'settings.lgdfs')
    
    _scenarios_to_translate_folder = os.path.join(_temp_path, 'omt_scenarios_to_translate')
    _translated_scenarios_folder = os.path.join(_temp_path, 'omt_translated_scenarios')
    
    _outputs_folder = os.path.join(_home_path, 'openmalariaTools')
    if not sys.platform == 'win32':
        _icon_path = os.path.join(_base_path, 'application', 'common', 'om.ico')
    else:
        _icon_path = os.path.join(_base_path, 'application', 'common', 'om.ico')
    
    _actual_schema_version = '23'
    
    @staticmethod
    def get_application_folder():
        return PathsAndSchema._application_folder
    
    @staticmethod
    def get_common_folder():
        return PathsAndSchema._common_folder
    
    @staticmethod
    def get_experiment_creator_path():
        return PathsAndSchema._experiment_creator_path
    
    @staticmethod
    def get_livegraph_path():
        return PathsAndSchema._livegraph_path
    
    @staticmethod
    def get_schema_translator_path():
        return PathsAndSchema._schema_translator_path
    
    @staticmethod
    def get_scenarios_to_translate_folder():
        return PathsAndSchema._scenarios_to_translate_folder
    
    @staticmethod
    def get_translated_scenarios_folder():
        return PathsAndSchema._translated_scenarios_folder
    
    @staticmethod
    def get_outputs_folder():
        return PathsAndSchema._outputs_folder
    
    @staticmethod
    def get_actual_schema():
        return PathsAndSchema._actual_schema_version
    
    @staticmethod
    def get_icon_path():
        return PathsAndSchema._icon_path
    
    @staticmethod
    def get_settings_file_path():
        return PathsAndSchema._settings_file_path
    
    
