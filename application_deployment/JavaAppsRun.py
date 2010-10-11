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
import time
import tempfile
import shutil

#from OpenMalariaRun import OpenMalariaRun

'''
ExperimentCreatorRun:
This class is used to start the experiment_creator.jar
java application'''
class ExperimentCreatorRun():
    
    actual_scenario_version = '21'
    
    base_folder = os.getcwd()
    experiment_creator_path = os.path.join(base_folder, 'application', 'experiment_creator', 'experiment_creator.jar')
    pid = ''
    
    '''
    start_experimentCreator:
    Starts the java program'''
    def start_experimentCreator(self, input_folder, output_folder, mainFileList, seeds_nr=0, validation=False, db_login = None, db_passwd = None, db_address = None):
        
        arglist = list()
        arglist.append('java')
        arglist.append('-jar')
        arglist.append(self.experiment_creator_path)
        
        if seeds_nr > 0:
            arglist.append('--seeds')
            arglist.append(str(seeds_nr))
        
        if not validation:    
            arglist.append('--no-validation')
            
        if db_login != None and db_passwd != None and db_address != None :
            arglist.append('--db')
            arglist.append('jdbc:mysql://'+db_address)
            arglist.append('--dbuser')
            arglist.append(db_login)
            arglist.append('--dbpasswdb')
            
            
        arglist.append(input_folder)
        arglist.append(output_folder)
        
        
        sub = subprocess.Popen (arglist)
        self.pid = sub.pid
        
        while(sub.poll()==None):
            time.sleep(.1)
        
        if os.path.exists(output_folder) and os.path.isdir(output_folder):
            files = os.listdir(output_folder)
            filenames = list()
            for file in files:
                file_split = str.split(file, '.')
                extension = file_split[len(file_split)-1]
                if extension == 'xml':
                    file_path = os.path.join(output_folder, file)
                    filenames.append(file_path)
                    
            if len(filenames)>0:
                #mainFileList.removeScenarios()
                mainFileList.addScenarios(filenames)
        
        
    
    '''quit_experimentCreator:
    Close the experimentCreator subprocess'''
    def quit_experimentCreator(self):
        if not (self.pid == ''):
            try:
                os.kill(self.pid, signal.SIGKILL)
                #self.kill_win(self.pid)
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

'''SchemaTranslatorRun:'''
class SchemaTranslatorRun():
    base_folder = os.getcwd()
    input_folder_path = os.path.join(base_folder, "translate_scenarios", "scenarios_to_translate")
    output_folder_path = os.path.join(base_folder,  "translate_scenarios","translated_scenarios")
    schema_translator_path = os.path.join(base_folder, "application", "schemaTranslator", "SchemaTranslator.jar")
    schema_folder = os.path.join(base_folder,  "application", "common") + '/' 
    
    def set_input_folder_path(self, input_folder_path):
        self.input_folder_path = input_folder_path
    
    def set_output_folder_path(self, output_folder_path):
        self.output_folder_path = output_folder_path
        
    def start_schematranslator_run_single(self, input_file_path):
        
        input_folder = os.path.split(input_file_path)[0]
        
        output_folder_path = os.path.join(input_folder, 'translated_to_schema_'+ExperimentCreatorRun.actual_scenario_version)
        if not os.path.exists(output_folder_path):
            os.mkdir(output_folder_path)
            
        temp_folder_path = tempfile.mkdtemp(dir=input_folder)
        shutil.copy2(input_file_path, temp_folder_path)
        
        arglist = list()
        arglist.append('java')
        arglist.append('-jar')
        arglist.append(self.schema_translator_path)
        arglist.append('--schema_folder')
        arglist.append(self.schema_folder)
        arglist.append('--input_folder')
        arglist.append(temp_folder_path)
        arglist.append('--output_folder')
        arglist.append(output_folder_path)
        
        sub = subprocess.Popen (arglist)
        
        while(sub.poll()==None):
            time.sleep(.1)
            
        shutil.rmtree(temp_folder_path, ignore_errors=True)
        
        return output_folder_path
        
        
        
