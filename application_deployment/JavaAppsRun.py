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
import ctypes

class ExperimentCreatorRun():
    base_folder = os.getcwd()
    experiment_creator_path = os.path.join(base_folder, 'application', 'experiment_creator', 'experiment_creator.jar')
    pid = ''
    
    def start_experimentCreator(self, input_path, output_path, seeds_nr = 0):
        thread = threading.Thread(group=None, target=self.start, args=(input_path, output_path, seeds_nr))
        thread.start()
        
    def start(self, input_path, output_path, seeds_nr):
        arglist = list()
        arglist.append('java')
        arglist.append('-jar')
        arglist.append(self.experiment_creator_path)
        
        if seeds_nr > 0:
            arglist.append('--seeds')
            arglist.append(seeds_nr)
            
        arglist.append('--no-validation')
            
        arglist.append(input_path)
        arglist.append(output_path)
        
        print "c'est parti!"
        
        self.pid = subprocess.Popen (arglist).pid
        
        print "c'est fini"
    
    '''quit_experimentCreator:
    Close the experimentCreator subprocess'''
    def quit_experimentCreator(self):
        if not (self.pid == ''):
            try:
                #os.kill(self.pid, signal.SIGKILL)
                self.kill_win(self.pid)
            except OSError:
                self.pid = ''
    
    '''kill_win: 
    Windows specific subprocess killing method'''
    def kill_win(self,pid):
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.OpenProcess(1, 0, pid)
        return (0 != kernel32.TerminateProcess(handle, 0)) 
        

'''
LiveGraphRun:
Helper class for starting a third party program
called LiveGraph. This program allows the user to
monitor the evolution of openmalaria's parameters''' 
class LiveGraphRun():
    base_folder = os.getcwd()
    live_graph_path= os.path.join(base_folder,'application', 'LiveGraph.2.0.beta01.Complete', 'LiveGraph.2.0.beta01.Complete.jar')
    settings_file_path = os.path.join(base_folder, 'application', 'common', 'settings.lgdfs')
    pid = ''
    
    '''
    start_livegraph:
    Starts the liveGraph Thread.'''
    def start_liveGraph(self, simPath, ctsoutPath):
        thread = threading.Thread(group=None,target=self.start, args=(simPath, ctsoutPath))
        thread.start()
    
    '''start: 
    creates the subprocess livegraph, modifies settings and starts the subprocess'''
    def start(self, simPath, ctsoutPath):
            
        self.quit_livegraph()
        
        src=open(self.settings_file_path)
        settings_string=src.read()
        src.close()
        
        settingsRE = re.compile('changeEntry')
        settings_string = settingsRE.sub('ctsout.txt', settings_string)
        
        dest= open(os.path.join(simPath,'settings.lgdfs'), 'w')
        dest.write(settings_string)
        dest.close()
        arglist = list()
        arglist.append('java')
        arglist.append('-jar')
        arglist.append(self.live_graph_path)
        arglist.append('-dfs')
        arglist.append(os.path.join(simPath, 'settings.lgdfs'))
        
        self.pid = subprocess.Popen (arglist, cwd=simPath).pid
    
    '''quit_livegraph:
    Close the livegraph subprocess'''
    def quit_livegraph(self):
        if not (self.pid == ''):
            try:
                #os.kill(self.pid, signal.SIGKILL)
                self.kill_win(self.pid)
            except OSError:
                self.pid = ''
    
    '''kill_win: 
    Windows specific subprocess killing method'''
    def kill_win(self,pid):
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.OpenProcess(1, 0, pid)
        return (0 != kernel32.TerminateProcess(handle, 0))  

'''SchemaTranslatorRun:
Deprecated, this object should allow the user 
to use the SchemaTranslator. This will be implemented later'''
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
        
        
        
