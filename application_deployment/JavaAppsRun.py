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
import re
import subprocess
import signal

class LiveGraphRun():
    base_folder = os.getcwd()
    live_graph_path= base_folder+"/application/LiveGraph.1.14.Complete/LiveGraph.1.14.Complete.jar"
    settings_file_path = base_folder +"/application/common/settings.lgdfs"
    pid = ''
    
    def start_liveGraph(self, simPath, ctsoutPath):
        
        self.quit_livegraph()
        
        src=open(self.settings_file_path)
        settings_string=src.read()
        src.close()
        
        settingsRE = re.compile('changeEntry')
        settings_string = settingsRE.sub(ctsoutPath, settings_string)
        
        dest= open(simPath+"/settings.lgdfs", 'w')
        dest.write(settings_string)
        dest.close()
        
        self.pid = subprocess.Popen ("java -jar "+self.live_graph_path +" -dfs "+simPath+"/settings.lgdfs", shell=True).pid
        
        print self.pid
    
    def quit_livegraph(self):
        if not (self.pid == ''):
            try:
                os.kill(self.pid, signal.SIGKILL)
            except OSError:
                self.pid = ''    

class SchemaTranslatorRun():
    base_folder = os.getcwd()
    input_folder_path = base_folder + "/translate_scenarios/scenarios_to_translate"
    output_folder_path = base_folder + "/translate_scenarios/translated_scenarios"
    schema_translator_folder = base_folder + "/application/schemaTranslator/SchemaTranslator.jar"
    schema_folder = base_folder + "/application/common/"  
    
    def set_input_folder_path(self, input_folder_path):
        self.input_folder_path = input_folder_path
    
    def set_output_folder_path(self, output_folder_path):
        self.output_folder_path = output_folder_path
        
    def get_schemaTranslator_command(self):
            return "java -jar "+self.schema_translator_folder+" --schema_folder "+self.schema_folder+" --input_folder "+self.input_folder_path+" --output_folder "+self.output_folder_path
        
        
        
