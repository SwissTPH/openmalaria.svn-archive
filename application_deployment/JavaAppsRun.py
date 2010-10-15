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
import pygtk
pygtk.require('2.0')
import gtk
import string

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

'''SchemaTranslatorRun:
Starts the java SchemaTranslator tool'''
class SchemaTranslatorRun():
    base_folder = os.getcwd()
    input_folder_path = os.path.join(base_folder, "translate_scenarios", "scenarios_to_translate")
    output_folder_path = os.path.join(base_folder,  "translate_scenarios","translated_scenarios")
    schema_translator_path = os.path.join(base_folder, "application", "schemaTranslator", "SchemaTranslator.jar")
    schema_folder = os.path.join(base_folder,  "application", "common") + '/' 
    
    IS_USING_CORRECT_SCENARIO_VERSION = 0
    IS_TRANSLATABLE = 1
    IS_NOT_TRANSLATABLE = -1
    NOT_FOUND = -2
    
    def set_input_folder_path(self, input_folder_path):
        self.input_folder_path = input_folder_path
    
    def set_output_folder_path(self, output_folder_path):
        self.output_folder_path = output_folder_path
    
    '''
    start_schematranslator_run:
    Copies all the input files in a temporary folder.
    The translated scenarios are then stored in a temporary output folder before being copied to the
    initial input folder. This is done so to avoid starting the schema translator for every loaded scenario
    '''    
    def start_schematranslator_run(self, input_files_paths):
        
        temp_input_folder_path = tempfile.mkdtemp(dir=self.input_folder_path)
        temp_output_folder_path = tempfile.mkdtemp(dir=self.output_folder_path)
        
        for input_file_path in input_files_paths:
            shutil.copy2(input_file_path[1], temp_input_folder_path)
        
        arglist = list()
        arglist.append('java')
        arglist.append('-jar')
        arglist.append(self.schema_translator_path)
        arglist.append('--schema_folder')
        arglist.append(self.schema_folder)
        arglist.append('--input_folder')
        arglist.append(temp_input_folder_path)
        arglist.append('--output_folder')
        arglist.append(temp_output_folder_path)
        
        sub = subprocess.Popen (arglist)
        
        while(sub.poll()==None):
            time.sleep(.1)
        
        output_files_infos_list = list()
            
        for input_file_path in input_files_paths:
            input_folder_path, input_file_name = os.path.split(input_file_path[1])
            temp_output_file_path = os.path.join(temp_output_folder_path, input_file_name)
            if os.path.exists(temp_output_file_path) and os.path.isfile(temp_output_file_path):
                output_folder_path = os.path.join(input_folder_path, 'translated_to_schema_'+ExperimentCreatorRun.actual_scenario_version)
                if not os.path.exists(output_folder_path):
                    os.mkdir(output_folder_path)
                output_file_infos = list()
                shutil.copy2(temp_output_file_path, output_folder_path)
                short_name, extension = os.path.splitext(input_file_name)
                output_file_infos.append(short_name)
                output_file_infos.append(os.path.join(output_folder_path, input_file_name))
                output_files_infos_list.append(output_file_infos)
                
            
        shutil.rmtree(temp_input_folder_path, ignore_errors=True)
        shutil.rmtree(temp_output_folder_path, ignore_errors=True)
        
        print len(output_files_infos_list)
        return output_files_infos_list
    
    '''
    check_and_return_runnable_scenarios:
    Checks if the given scenarios are usable with the actual schema version and then returns the list of runnable scenarios.
    '''
    def check_and_return_runnable_scenarios(self, scenario_infos_list, parent_window = None, added_message=None):
        right_version_scenarios = list()
        wrong_version_not_translatable_scenarios = list()
        wrong_version_translatable_scenarios = list()
        not_found_scenarios = list()
        
        for scenario_infos in scenario_infos_list:
            scenario_check = self.check_scenario_version(scenario_infos[1])
            if(scenario_check == self.IS_USING_CORRECT_SCENARIO_VERSION):
                right_version_scenarios.append(scenario_infos)
            elif(scenario_check == self.IS_TRANSLATABLE):
                wrong_version_translatable_scenarios.append(scenario_infos)
            elif(scenario_check == self.IS_NOT_TRANSLATABLE):
                wrong_version_not_translatable_scenarios.append(scenario_infos)
            else:
                not_found_scenarios.append(scenario_infos)
        
     
        self.show_import_problems_message(parent_window, wrong_version_not_translatable_scenarios, wrong_version_translatable_scenarios, not_found_scenarios, added_message)
        
        if(len(self.translated_files)>0):
            right_version_scenarios.extend(self.translated_files)
        
        for right_version_scenario in right_version_scenarios:
            self.correct_schema_file_name(right_version_scenario[1])
        
        return right_version_scenarios
    
    '''
    init_translation:
    Initializes the translation if the user press ok on the message dialog'''
    def init_translation(self, dialog, response_id, wvts):
        if response_id == gtk.RESPONSE_YES:
            self.translated_files = self.start_schematranslator_run(wvts)
            
    
    '''
    check_scenario_version:
    checks whether or not the loaded scenario schema version is supported
    by the openmalaria application. If the schema version is higher than
    the one used by the openmalaria application, then this schema can't be used
    at all and no translation is possible. On an other hand, if the schema version
    is lower than the one used by the openmalaria application, then in some cases,
    a translation is possible.'''
    def check_scenario_version(self,scenario_path):
        if os.path.exists(scenario_path) and os.path.isfile(scenario_path):
            src=open(scenario_path)
            file_string=src.read()
            src.close()
            
            search_match = re.search(r'(?P<schema_text_1>schemaVersion=")(?P<schema_version>\d+)(?P<schema_text_2>")', file_string)
            
            if search_match == None:
                return self.IS_NOT_TRANSLATABLE
            else:
                try:
                    schema_vers = int(search_match.group('schema_version'))
                    if schema_vers > int(ExperimentCreatorRun.actual_scenario_version):
                        return self.IS_NOT_TRANSLATABLE
                    elif schema_vers < int(ExperimentCreatorRun.actual_scenario_version):
                        return self.IS_TRANSLATABLE
                    else:
                        return self.IS_USING_CORRECT_SCENARIO_VERSION   
                except exceptions.ValueError:
                    return self.IS_NOT_TRANSLATABLE
        else:
            return self.NOT_FOUND
    
    '''
    correct_schema_file_name:
    Sets the schema_file_name (after having checked that the schema version is the same as the one used by the openmalaria application) to
    a name that will be recognized by the application'''    
    def correct_schema_file_name(self,scenario_path):
        if os.path.exists(scenario_path) and os.path.isfile(scenario_path):
            src=open(scenario_path)
            file_string=src.read()
            src.close()
            
            file_string = re.sub(r'SchemaLocation="scenario.xsd"', 'SchemaLocation="scenario_'+ExperimentCreatorRun.actual_scenario_version+'.xsd"', file_string)
            
            dest=open(scenario_path,'w')
            dest.write(file_string)
            dest.close()
        

    '''
    show_import_problems_message:
    Shows the found problems during the importation of some scenarios in openMalariaTools'''
    def show_import_problems_message(self, parent_window, wvnts, wvts, nfs, added_message):
        
        self.translated_files = list()
        
        if len(wvts) > 0:
            problems = ''
            if not added_message == None:
                problems = added_message + '\n'
            
            problems += str(len(wvts)) + " scenarios are using an older (possibly translatable) schema version. Would you like that the system tries to update the scenarios using an older schema version? "
            import_problems_message = gtk.MessageDialog(parent_window, gtk.DIALOG_MODAL,gtk.MESSAGE_WARNING,gtk.BUTTONS_NONE, problems)
            import_problems_message.add_button('Yes', gtk.RESPONSE_YES)
            import_problems_message.add_button('No', gtk.RESPONSE_NO)
            import_problems_message.connect('response', self.init_translation, wvts)
            import_problems_message.run()
            import_problems_message.destroy()
            
        if len(wvnts)>0:
            error_message = ''
            if not added_message == None:
                error_message = added_message + '\n'
            
            error_message += str(len(wvnts)) + " scenarios are using an unsupported schema version. You will not be able to run these scenarios. Please try to update to a newest version of openmalariaTools..."
            import_error_message = gtk.MessageDialog(self.parent_window, gtk.DIALOG_MODAL,gtk.MESSAGE_ERROR,gtk.BUTTONS_NONE, problems)
            import_error_message.add_button('Ok', gtk.RESPONSE_OK)
            import_error_message.run()
            import_error_message.destroy()
        
        
