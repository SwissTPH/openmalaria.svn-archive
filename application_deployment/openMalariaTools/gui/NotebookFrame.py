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

import sys
import os
import pygtk
if not sys.platform == 'win32':
    pygtk.require('2.0')
import gtk
import time

from FileListFrame import FileList
from VirtualTerminal_win import VirtualTerminal_win
from ActualScenariosFoldersFrame import ActualScenariosFolders
from ExperimentCreatorDialog import ExperimentCreatorDialog
from FileViewersContainerDialog import FileViewersContainer
from ScenariosChoiceDialog import ScenariosChoice

from ..tools_management.JavaAppsRun import LiveGraphRun
from ..tools_management.OpenMalariaRun import OpenMalariaRun
from ..utils.PathsAndSchema import PathsAndSchema

'''
This class helps to build
for this application standardized frames (main window)
using three lines (top, middle, bottom).
top line: Load buttons, option buttons
middle line: Terminal
bottom line: Start/Stop buttons
'''
class NotebookFrame(gtk.Frame):
    
    def __init__(self, frame_name, parent, isWindows = False):
        gtk.Frame.__init__(self, frame_name)
        self.vertical_box = gtk.VBox(False, 10)
        self.vertical_box.show()
        self.lines_boxes = list()
        self.parent_window = parent
        self.fileList = FileList(self.parent_window,False,self)
        
        for i in range(4):
            self.lines_boxes.append(gtk.HBox(False, 7))
            self.lines_boxes[i].show() 
        
        self.vertical_box.pack_start(self.lines_boxes[0], False, False, 0)
        self.vertical_box.pack_start(self.lines_boxes[1], False, False, 0)
        self.vertical_box.pack_start(self.lines_boxes[2], True, True, 0)
        self.vertical_box.pack_start(self.lines_boxes[3], False, False, 0)
        
        self.add(self.vertical_box)
        
        self.first_option = True
        self.first_start_button = True
        self.first_stop_button = True
        self.first_terminal = True
        self.first_popSize_entry = True
        self.isWindows = isWindows
        
        self.sim_option_popsize = gtk.Entry()
        self.options = list()
        
        base_folder = os.getcwd()
        
        self.run_scenarios_outputs = PathsAndSchema.get_outputs_folder()
        self.liveGraphRun = LiveGraphRun()
        self.openMalariaRun = OpenMalariaRun()
        self.load_allready_open = False
        self.creator_allready_open = False
            
        self.stop_run = False
    
    '''
    openMalariaCommand:
    This function prepare the commands for the OpenMalariaRun object.
    This handles batch jobs too'''
    def openMalariaCommand(self, widget, data=None):
        selected = self.fileList.get_selected_filenames()
        self.fileList.reset_simulation_state()
        self.is_running = True
        filenames = selected[0]
        names = selected[1]
        iterators = selected[2]
        
        self.enable_stop_button()
        NotebookFrame.start_button.set_sensitive(False)
        
        checkpointing = False
        nocleanup = False
        use_livegraph = False
        only_one_folder = False
        custom_pop_size = False
        pop_size = 0
        
        for i in range(len(self.options)):
            option = self.options[i]
            if(option[0].get_active()):
                if(option[1]=='--liveGraph'):
                    use_livegraph = True
                elif(option[1]=='-- --checkpoint'):
                    checkpointing = True
                elif(option[1]=='-c'):
                    nocleanup = True
                elif(option[1]=='only_one_folder'):
                    only_one_folder = True
                    name = "batch_run_"+time.strftime("%d_%b_%Y_%H%M%S")
                    simDir= os.path.join(self.run_scenarios_outputs,name)
                    os.mkdir(simDir)
                elif(option[1]=='custom_population_size'):
                    popsize_string = self.sim_population_size_entry.get_text()
                    custom_pop_size = True
                    try:
                        pop_size = int(popsize_string)
                    except exceptions.ValueError:
                        pop_size = -1
        
        i = 0            
        while i < len(filenames) and self.is_running:
            if not only_one_folder:
                simDir = os.path.join(self.run_scenarios_outputs,names[i]+'_'+time.strftime("%d_%b_%Y_%H%M%S"))
                os.mkdir(simDir)
            if i == 0:
                newBuffer = True
            else:
                newBuffer = False    
            run_feedback = self.openMalariaRun.runScenario(self.terminal, self.liveGraphRun, filenames[i], names[i], simDir, only_one_folder, pop_size, custom_pop_size, checkpointing, nocleanup, use_livegraph, newBuffer)
            if not only_one_folder:
                if(self.stop_run):
                    self.stop_run = False
                elif run_feedback:
                    self.actualScenariosFolders.add_folder(simDir, names[i])
            self.fileList.set_simulation_state(run_feedback, iterators[i])
            i += 1
        
        if only_one_folder:
            self.actualScenariosFolders.add_folder(simDir,name)
        
        NotebookFrame.start_button.set_sensitive(True)
        self.disable_stop_button()  
    
    '''
    schemaTranslatorCommand:
    This function is deprecated and will only work on linux. This should be
    changed in a later version. This command calls the vte Terminal emulator
    and starts the schema translator.'''
    def schemaTranslatorCommand(self, widget, data=None):
        command = self.schemaTranslatorRun.get_schemaTranslator_command()
        
        for i in range(len(self.options)):
            option = self.options[i]
            if(option[0].get_active()):
                command = command +' '+option[1]
                  
        self.terminal.run_command(command)
    
    '''
    openNewDialog:
    Opens a new File Chooser, so the user can choose what files he would like
    to load in the tool'''
    def openNewDialog(self, widget, data=None):
        if not self.load_allready_open:
            self.scenarioChoice = ScenariosChoice(self.fileList, self.parent_window, self)
            self.load_allready_open = True
    
    '''
    add_object:
    Adds a widget in the window. The user just need to define 
    on which line/row (There are three lines/rows) he would like to
    put his new widget'''
    def add_object(self, line_number, window_object, at_start_h=True, resize=False):
            
        if(at_start_h):
            self.lines_boxes[line_number].pack_start(window_object, resize, resize,2)
        else:
            self.lines_boxes[line_number].pack_end(window_object, resize, resize,2)
        
        window_object.show()
    
    '''
    add_population_size_entry:
    Adds an entry and a checkbox widget to the tool.
    This entry is used for setting custom population's sizes'''
    def add_population_size_entry(self, line_number=0, at_start_h=True, resize=False):
        sim_population_size_vbox = gtk.VBox(False, 2)
        sim_population_size_label = gtk.Label('')
        sim_population_size_label.set_alignment(0,0)
        
        sim_population_size_hbox = gtk.HBox(False, 2)
        self.sim_population_size_entry = gtk.Entry(25)
        self.sim_population_size_entry.set_text('100')
        self.sim_population_size_entry.set_sensitive(False)
        sim_population_size_checkbox = gtk.CheckButton('Custom population size ', False)
        sim_population_size_hbox.pack_start(sim_population_size_checkbox, False, False, 2)
        sim_population_size_hbox.pack_start(self.sim_population_size_entry, False, False, 2)
        
        sim_population_size_vbox.pack_start(sim_population_size_label, False, False, 2)
        sim_population_size_vbox.pack_start(sim_population_size_hbox, False, False, 2)
        sim_population_size_vbox.show_all()
        
        sim_population_size_checkbox.connect('toggled', self.change_sim_population_size_entry_state)
        actual_option = [sim_population_size_checkbox, 'custom_population_size']
        self.options.append(actual_option)
        
        self.add_object(line_number, sim_population_size_vbox, at_start_h)
    
    '''
    change_sim_population_size_entry_state:
    changes the population size's option toggle button state'''
    def change_sim_population_size_entry_state(self, widget):
        self.sim_population_size_entry.set_sensitive(widget.get_active())
        
    '''
    add_output_folder_button:
    Adds a button and an entry that permits the user to choose the output folder'''
    def add_output_folder_button(self, line_number=1, at_start_h=True):
        
        self.output_folder_chooser_opened = False
        
        output_folder_button_vbox = gtk.VBox(False, 2)
        output_folder_label = gtk.Label('Select Output folder')
        output_folder_label.set_alignment(0,0)
        
        output_folder_button_hbox = gtk.HBox(False, 2)
        output_folder_button = gtk.Button("Select...")
        output_folder_entry = gtk.Entry(65535)
        output_folder_entry.set_text(self.run_scenarios_outputs)
        #output_folder_entry.set_width_chars(400)
        output_folder_entry.set_sensitive(False)
        output_folder_button.connect('clicked', self.open_output_folder_chooser, output_folder_entry)
        output_folder_button_hbox.pack_start(output_folder_button, False, False, 0)
        output_folder_button_hbox.pack_start(output_folder_entry, True, True, 2)
        
        output_folder_button_vbox.pack_start(output_folder_label, True, True, 2)
        output_folder_button_vbox.pack_start(output_folder_button_hbox, True, True, 2)
        output_folder_button_vbox.show_all()
        
        self.add_object(line_number, output_folder_button_vbox, at_start_h, True)
    
    '''
    open_output_folder_chooser:
    Opens a folder chooser dialog'''
    def open_output_folder_chooser(self, widget, entry):
        if not self.output_folder_chooser_opened:
            self.output_folder_chooser_opened = True
            folder_chooser = gtk.FileChooserDialog('Choose output folder', self.parent, gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER, ('ok',gtk.RESPONSE_OK)) 
            icon_path = PathsAndSchema.get_icon_path()
            folder_chooser.set_icon_from_file(icon_path)
            folder_chooser.connect('response', self.select_output_folder, entry)
            folder_chooser.connect('destroy', self.allow_open_output_folder_chooser)
            folder_chooser.show()
    
    '''
    allow_open_output_folder_chooser:
    This function is used to prevent multiple chooser openings'''
    def allow_open_output_folder_chooser(self, widget, data=None):
        self.output_folder_chooser_opened = False
    
    '''
    select_output_folder:
    If the user clicks ok, then the actual output folder path is
    the same as the selected folder in the chooser'''
    def select_output_folder(self, widget, response_id, entry):
        if response_id == gtk.RESPONSE_OK:
            self.run_scenarios_outputs = widget.get_filename()
            entry.set_text(self.run_scenarios_outputs)
            widget.destroy()  
   
    '''
    add_terminal:
    Adds a terminal to output the simulations status during the runs''' 
    def add_terminal(self, line_number=2, at_start_h=True, resize=True):
        if(self.first_terminal):
            terminal_hbox = gtk.HBox(False, 2)
            
            if self.isWindows:
                self.terminal = VirtualTerminal_win()
            else:
                self.terminal = VirtualTerminal()
                
            terminal_hbox.pack_start(self.terminal, True, True, 0)
            self.terminal.show()
            
            self.first_terminal = False
            
            self.add_object(line_number, terminal_hbox, at_start_h, resize)
    
    '''
    add_file_list:
    Adds a FileList Frame to the actual window
    (See FileList class)'''
    def add_file_list(self, line_number=2, at_start_h=True, resize=False):
        self.add_object(line_number, self.fileList, at_start_h, resize)
    
    '''
    add_outputs_frame:
    Adds a ActualScenariosFolders Frame to the actual window 
    (See ActualScenariosFolders class)'''    
    def add_outputs_frame(self, line_number=3, at_start_h=True, resize=True):
        self.actualScenariosFolders = ActualScenariosFolders()
        self.add_object(line_number, self.actualScenariosFolders, at_start_h, resize)
    
    '''
    disable_stop_button:
    Disables the stop_button'''     
    def disable_stop_button(self):
        self.terminal_stop_button.set_sensitive(False)
    
    '''
    enable_stop_button:
    Enables stop button'''
    def enable_stop_button(self):
        self.terminal_stop_button.set_sensitive(True)
    
    '''
    add_option_button:
    Adds a  toggle option button for simulation's options'''
    def add_option_button(self, title, option_code, at_start_h=True, line_number=0):
        sim_option_vbox = gtk.VBox(False, 2)
        
        if(self.first_option):
            sim_option_label = gtk.Label("Options")
            self.first_option = False
        else:
            sim_option_label = gtk.Label("")    
        sim_option_label.set_alignment(0,0)
        sim_option_label.show()
        
        sim_option = gtk.CheckButton(title, False)
        sim_option.show()
        actual_option = [sim_option, option_code]
        self.options.append(actual_option)
        
        sim_option_vbox.pack_start(sim_option_label, False, False, 2)
        sim_option_vbox.pack_start(sim_option, False, False, 2)
        self.add_object(line_number, sim_option_vbox, at_start_h)
        
    '''
    add_livegraph_option:
    Adds the livegraph option that allows user to have a look at the
    variables and parameters changes during the simulation'''
    def add_livegraph_option(self, title, option_code, at_start_h=True, line_number=0):
        sim_option_vbox = gtk.VBox(False, 2)
        
        if(self.first_option):
            sim_option_label = gtk.Label("Options")
            self.first_option = False
        else:
            sim_option_label = gtk.Label("")    
        sim_option_label.set_alignment(0,0)
        sim_option_label.show()
        
        NotebookFrame.sim_option_livegraph = gtk.CheckButton(title, False)
        NotebookFrame.sim_option_livegraph.show()
        actual_option = [NotebookFrame.sim_option_livegraph, option_code]
        self.options.append(actual_option)
        
        sim_option_vbox.pack_start(sim_option_label, False, False, 2)
        sim_option_vbox.pack_start(NotebookFrame.sim_option_livegraph, False, False, 2)
        self.add_object(line_number, sim_option_vbox, at_start_h)
    
    '''
    add_import_button:
    Adds a load/import button to permit the opening of a new
    File Chooser dialog'''
    def add_import_button(self, at_start_h = True, line_number=0, descr="Load scenarios" , title="Load..."):
        sim_import_vbox = gtk.VBox(False,2)
        
        sim_import_label = gtk.Label(descr)
        sim_import_label.show()
        
        self.sim_import_button = gtk.Button(title)
        self.sim_import_button.connect('clicked', self.openNewDialog)
        self.sim_import_button.show()
        
        sim_import_vbox.pack_start(sim_import_label, False, False, 2)
        sim_import_vbox.pack_start(self.sim_import_button, False, False, 2)
        
        self.add_object(line_number, sim_import_vbox, at_start_h)
    
    '''
    add_start_button:
    Adds a start button for starting the simulations\batches'''
    def add_start_button(self, at_start_h=True, cbox_line_number=0, button_line_number=3, title="Start", simulator=True):
        if(self.first_start_button):
            if(simulator):
                vbox = gtk.VBox(False,2)
                sim_start_button_label = gtk.Label(title)
                hbox = gtk.HBox(False,2)
                NotebookFrame.start_button = gtk.Button()
                NotebookFrame.start_button.set_image(gtk.image_new_from_stock(gtk.STOCK_EXECUTE, gtk.ICON_SIZE_BUTTON))
                hbox.pack_start(NotebookFrame.start_button)
                hbox.show_all()
                vbox.pack_start(sim_start_button_label, False, False, 2)
                vbox.pack_start(hbox, False, False, 2)
                vbox.show_all()
                self.add_object(button_line_number, vbox, at_start_h)
                NotebookFrame.start_button.set_sensitive(True)
                NotebookFrame.start_button.connect('clicked', self.openMalariaCommand)
                
            else:
                start_button = gtk.Button(title)
                start_button.connect('clicked', self.schemaTranslatorCommand)
                self.add_object(button_line_number, start_button, at_start_h)
                
            self.first_start_button = False
        else:
            print("There is already an existing start button for this frame")
            
    
    '''
    add_stop_button:
    Adds a stop button for terminating the simulations\batches'''
    def add_stop_button(self, at_start_h=True, line_number=3, title="Stop"):
        if(self.first_stop_button):
            vbox = gtk.VBox(False,2)
            sim_stop_button_label = gtk.Label(title)
            hbox = gtk.HBox(False,2)
            self.terminal_stop_button = gtk.Button()
            self.terminal_stop_button.set_image(gtk.image_new_from_stock(gtk.STOCK_STOP, gtk.ICON_SIZE_BUTTON))
            hbox.pack_start(self.terminal_stop_button)
            hbox.show_all()
            vbox.pack_start(sim_stop_button_label, False, False, 2)
            vbox.pack_start(hbox, False, False, 2)
            vbox.show_all()
            self.add_object(line_number, vbox,at_start_h)
            self.terminal_stop_button.connect('clicked', self.reset_callback)
            self.terminal_stop_button.set_sensitive(False)
            self.first_stop_button = False
        else:
            print("There is already an existing stop button for this frame")
            
        
    '''
    add_experiment_creator_button:
    Adds a button to open an experiment creator dialog '''
    def add_experiment_creator_button(self, at_start_h = True, line_number=0, descr="Create Experiment" , title="Create..."):
        sim_import_vbox = gtk.VBox(False,2)
        
        sim_import_label = gtk.Label(descr)
        sim_import_label.show()
        
        self.sim_import_button = gtk.Button(title)
        self.sim_import_button.connect('clicked', self.open_new_experiment_creator_dialog)
        self.sim_import_button.show()
        
        sim_import_vbox.pack_start(sim_import_label, False, False, 2)
        sim_import_vbox.pack_start(self.sim_import_button, False, False, 2)
        
        self.add_object(line_number, sim_import_vbox, at_start_h)
    
    '''
    open_new_experiment_creator_dialog:
    Opens a new experiment creator dialog''' 
    def open_new_experiment_creator_dialog(self, widget, data=None):
        if not self.creator_allready_open:
            ExperimentCreatorDialog(self.fileList, self.parent_window, self)
            self.creator_allready_open = True
    
    '''
    reset_callback:
    Does a reset callback on the terminal object'''
    def reset_callback(self, widget, data=None):
        self.terminal.run_reset_callback()
        self.is_running = False