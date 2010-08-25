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
import threading

class LiveGraphRun():
    base_folder = os.getcwd()
    live_graph_path= os.path.join(base_folder,'application', 'LiveGraph.2.0.beta01.Complete', 'LiveGraph.2.0.beta01.Complete.jar')
    settings_file_path = os.path.join(base_folder, 'application', 'common', 'settings.lgdfs')
    pid = ''
    
    def start_liveGraph(self, simPath, ctsoutPath):
        thread = threading.Thread(group=None,target=self.start, args=(simPath, ctsoutPath))
        thread.start()
    
    def start(self, simPath, ctsoutPath):
        
        print simPath
        
        self.quit_livegraph()
        
        src=open(self.settings_file_path)
        settings_string=src.read()
        src.close()
        
        settingsRE = re.compile('changeEntry')
        print settings_string
        print ctsoutPath
        
        settings_string = settingsRE.sub('ctsout.txt', settings_string)
        print settings_string
        
        dest= open(os.path.join(simPath,'settings.lgdfs'), 'w')
        dest.write(settings_string)
        dest.close()
        
        self.pid = subprocess.Popen ("java -jar "+self.live_graph_path +" -dfs "+os.path.join(simPath, 'settings.lgdfs'), shell=True, cwd=simPath).pid
        
        print self.pid
    
    def quit_livegraph(self):
        if not (self.pid == ''):
            try:
                #os.kill(self.pid, signal.SIGKILL)
                self.kill_win(self.pid)
            except OSError:
                self.pid = ''
                
    def kill_win(self,pid):
        import win32api
        handle = win32api.OpenProcess(1,0,pid)
        return (0 != win32api.TerminateProcess(handle, 0))    

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
        
        
        
