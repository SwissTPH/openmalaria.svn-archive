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

import pygtk
pygtk.require('2.0')
import gtk
import os
import fnmatch
import string
import re
import sys
import tempfile

from VirtualTerminal import VirtualTerminal
from OpenMalariaRun import OpenMalariaRun
from JavaAppsRun import SchemaTranslatorRun
from JavaAppsRun import LiveGraphRun

class ScenariosChoice(gtk.Window):
    def __init__(self):
        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
        self.set_border_width(10)
        self.scenarios_widget = gtk.FileChooserWidget()
        
        
        #self.scenarios_widget.set_default_response(gtk.RESPONSE_OK)
        base_folder = os.getcwd()
        run_scenarios_base = base_folder + "/run_scenarios/scenarios_to_run"
        self.scenarios_widget.set_select_multiple(True)
        self.scenarios_widget.set_current_folder(run_scenarios_base)
        '''list = self.scenarios_widget.get_children()
        list = list[0].get_children()
        list = list[0].get_children()
        
        for item in list:
            print(item)'''
        
        '''filter = gtk.FileFilter()
        filter.set_name("All files")
        filter.add_pattern("*")
        self.scenarios_widget.add_filter(filter)'''
        
        filter = gtk.FileFilter()
        filter.set_name("Xml files")
        filter.add_pattern("*.xml")
        self.scenarios_widget.add_filter(filter)
        
        self.scenarios_widget.show()
        self.set_title("Scenarios to run...")
        self.add(self.scenarios_widget)
    
    def get_actual_selection(self):
        return self.scenarios_widget.get_filenames()

class NotebookFrame(gtk.Frame):
    def __init__(self, frame_name, isSimulatorFrame = True):
        gtk.Frame.__init__(self, frame_name)
        
        self.vertical_box = gtk.VBox(False, 10)
        self.vertical_box.show()
        self.lines_boxes = list()
        
        for i in range(3):
            self.lines_boxes.append(gtk.HBox(False, 5))
            self.lines_boxes[i].show() 
        
        self.vertical_box.pack_start(self.lines_boxes[0], False, False, 0)
        self.vertical_box.pack_start(self.lines_boxes[1], True, True, 0)
        self.vertical_box.pack_start(self.lines_boxes[2], False, False, 0)
        
        self.add(self.vertical_box)
        
        self.first_option = True
        self.first_start_button = True
        self.first_stop_button = True
        self.first_terminal = True
        self.first_popSize_entry = True
        
        self.sim_option_popsize = gtk.Entry()
        self.options = list()
        
        base_folder = os.getcwd()
        
        if(isSimulatorFrame):
            self.run_scenarios_base = base_folder + "/run_scenarios/scenarios_to_run"
            self.run_scenarios_outputs = base_folder + "/run_scenarios/outputs"
            self.liveGraphRun = LiveGraphRun()
            self.openMalariaRun = OpenMalariaRun()
        else:
            self.run_scenarios_base = base_folder +"/translate_scenarios/scenarios_to_translate"
            self.schemaTranslatorRun = SchemaTranslatorRun()
            
        
        self.isSimulatorFrame = isSimulatorFrame
    
    def get_scenarios_combobox(self):
        sim_cbox = gtk.combo_box_new_text()
        for filename in os.listdir(self.run_scenarios_base):
                if fnmatch.fnmatch(filename, "*.xml"):
                  sim_cbox.append_text(string.split(filename,"scenario")[1])
        return sim_cbox
    
    def openMalariaCommand(self, widget, data=None):
        
        self.update_popSize_scenario()
        scenario_string = string.split(self.sim_cbox.get_active_text(), '.')[0]
        
        
        checkpointing = False
        nocleanup = False
        use_livegraph = False
        
        for i in range(len(self.options)):
            option = self.options[i]
            if(option[0].get_active()):
                if(option[1]=='--liveGraph'):
                    use_livegraph = True
                elif(option[1]=='-- --checkpoint'):
                    checkpointing = True
                elif(option[1]=='-c'):
                    nocleanup = True
        
        self.openMalariaRun.runScenario(self.terminal, self.liveGraphRun, scenario_string, checkpointing, nocleanup, use_livegraph)
    
    
    def schemaTranslatorCommand(self, widget, data=None):
        #command = './run.py -t'
        command = self.schemaTranslatorRun.get_schemaTranslator_command()
        
        for i in range(len(self.options)):
            option = self.options[i]
            if(option[0].get_active()):
                command = command +' '+option[1]
                  
        self.terminal.run_command(command)
    
    def importScenario(self, widget, data=None):
        imported_path = self.sim_import_button.get_filename()
        imported_split = string.split(imported_path, "/")
        imported_name = imported_split[len(imported_split)-1]
        
        src=open(imported_path)
        scen_string=src.read()
        src.close()
        
        filenames = list()
        
        for filename in os.listdir(self.run_scenarios_base):
            filenames.append(filename)
            
        test_filename = imported_name
        i = 1
        
        while(filenames.count(test_filename)>0):
            test_split = string.split(imported_name, '.')
            test_filename = test_split[0] + '_'+str(i)+'.'+test_split[1]
            i = i + 1
            
        imported_name = test_filename      
    
        dest= open(self.run_scenarios_base+'/'+imported_name, 'w')
        dest.write(scen_string)
        dest.close()
        
        if(self.isSimulatorFrame):
            self.sim_cbox.append_text(string.split(imported_name, "scenario")[1])
    
    def update_popSize_scenario(self, data=None):
        filename = 'scenario' + self.sim_cbox.get_active_text()
        
        src=open(self.run_scenarios_base +'/'+ filename)
        pop_string=src.read()
        src.close()
        
        popSizeRE = re.compile('popSize="\d*"')
        popSizeString = popSizeRE.findall(pop_string)[0]
        popSizeString = popSizeString[len('popSize="'):len(popSizeString)-1]
        
        if not(popSizeString == self.sim_option_popsize.get_text()):
            pop_string = popSizeRE.sub('popSize="'+self.sim_option_popsize.get_text()+'"', pop_string)
            dest= open(self.run_scenarios_base +'/'+ filename, 'w')
            dest.write(pop_string)
            dest.close()
    
    def add_object(self, line_number, window_object, at_start_h=True, resize=False):
            
        if(at_start_h):
            self.lines_boxes[line_number].pack_start(window_object, resize, resize)
        else:
            self.lines_boxes[line_number].pack_end(window_object, resize, resize)
        
        window_object.show()
    
    def add_terminal(self, line_number=1, at_start_h=True, resize=True):
        if(self.first_terminal):
            terminal_hbox = gtk.HBox(False, 2)
            
            self.terminal = VirtualTerminal()
            terminal_hbox.pack_start(self.terminal, True, True, 0)
            self.terminal.show()
            
            self.first_terminal = False
            
            self.add_object(line_number, terminal_hbox, at_start_h, resize)
    
    def open_multiple_scenarios_dialog(self, widget, data=None):
        dialog = gtk.FileChooserdialog("Use..",None,gtk.FILE_CHOOSER_ACTION_OPEN,(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)
        dialog.set_select_multiple(True)
        
        filter = gtk.FileFilter()
        filter.set_name("All files")
        filter.add_pattern("*")
        dialog.add_filter(filter)
        
        filter = gtk.FileFilter()
        filter.set_name("Xml files")
        filter.add_pattern("*.xml")
        dialog.add_filter(filter)
        
        dialog.show()        
    
    def add_multiple_scenarios_button(self, at_start_h = True, line_number=0, descr="Use scenarios..." , title="Use..."):
        sim_import_vbox = gtk.VBox(False,2)
        
        sim_import_label = gtk.Label(descr)
        sim_import_label.show()
        
        self.sim_import_button = gtk.Button(title)
        self.sim_import_button.connect('clicked', self.open_multiple_scenarios_dialog)
        self.sim_import_button.show()
        
        sim_import_vbox.pack_start(sim_import_label, False, False, 2)
        sim_import_vbox.pack_start(self.sim_import_button, False, False, 2)
        
        self.add_object(line_number, sim_import_vbox, at_start_h)
    
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
    
    def add_import_button(self, at_start_h = True, line_number=0, descr="Import scenario" , title="Import..."):
        sim_import_vbox = gtk.VBox(False,2)
        
        sim_import_label = gtk.Label(descr)
        sim_import_label.show()
        
        self.sim_import_button = gtk.FileChooserButton(title)
        self.sim_import_button.connect('file-set', self.importScenario)
        self.sim_import_button.show()
        
        sim_import_vbox.pack_start(sim_import_label, False, False, 2)
        sim_import_vbox.pack_start(self.sim_import_button, False, False, 2)
        
        self.add_object(line_number, sim_import_vbox, at_start_h)
    
    def add_scenario_cbox(self, at_start_h = True, line_number=0):
        sim_cbox_vbox = gtk.VBox(False, 2)
        
        sim_cbox_label = gtk.Label('Scenario')
        sim_cbox_label.set_alignment(0,0) 
        sim_cbox_label.show()
        
        self.sim_cbox = self.get_scenarios_combobox()
        self.sim_cbox.connect('changed', self.update_popSize_entry)
        self.sim_cbox.set_active(0)
        self.sim_cbox.show()
        
        sim_cbox_vbox.pack_start(sim_cbox_label, False, False, 2)
        sim_cbox_vbox.pack_start(self.sim_cbox, False, False, 2)
        
        self.add_object(line_number, sim_cbox_vbox, at_start_h)
        
    def update_popSize_entry(self, widget, data=None):
        filename = 'scenario' + self.sim_cbox.get_active_text()
            
        src=open(self.run_scenarios_base +'/'+ filename)
        pop_string=src.read()
        src.close()
        
        popSizeRE = re.compile('popSize="\d*"')
        popSizeString = popSizeRE.findall(pop_string)[0]
        popSizeString = popSizeString[len('popSize="'):len(popSizeString)-1]
        
        self.sim_option_popsize.set_text(popSizeString)
        
    def add_popSize_entry(self, at_start_h = True, line_number=0):
        if(self.first_popSize_entry):
            
            sim_entry_vbox = gtk.VBox(False, 2)

            sim_entry_label = gtk.Label('Population Size')
            self.update_popSize_entry
            sim_entry_label.set_alignment(0,0)
            sim_entry_label.show()
            self.sim_option_popsize.show()
            
            sim_entry_vbox.pack_start(sim_entry_label, False, False, 2)
            sim_entry_vbox.pack_start(self.sim_option_popsize, False, False, 2)
            
            self.first_popSize_entry = False
            
            self.add_object(line_number, sim_entry_vbox, at_start_h)     
    
    def add_start_button(self, at_start_h=True, cbox_line_number=0, button_line_number=2, title="Start", simulator=True):
        if(self.first_start_button):
            if(simulator):
                start_button = gtk.Button(title)
                self.start_cbox = self.add_scenario_cbox(at_start_h, cbox_line_number)
                start_button.connect('clicked', self.openMalariaCommand)
                self.add_object(button_line_number, start_button, at_start_h)
            else:
                start_button = gtk.Button(title)
                start_button.connect('clicked', self.schemaTranslatorCommand)
                self.add_object(button_line_number, start_button, at_start_h)
                
            self.first_start_button = False
        else:
            print("There is already an existing start button for this frame")
            
    
    def add_stop_button(self, at_start_h=True, line_number=2, tite="Stop"):
        if(self.first_stop_button):
            terminal_stop_button = gtk.Button("Stop")
            terminal_stop_button.connect('clicked', self.terminal.run_reset_callback)
            self.add_object(line_number, terminal_stop_button,at_start_h)
            self.first_stop_button = False
        else:
            print("There is already an existing stop button for this frame")


class OMFrontend:
    
    def delete_event(self, widget, event, data=None):
        return False
    
    def destroy(self, widget, data=None):
        gtk.main_quit()
        sys.exit()
        
        
    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect("delete_event", self.delete_event)
        self.window.connect("destroy", self.destroy)
        self.window.set_border_width(10)
        self.window.set_title("openMalaria Tools")
        
        #notebook
        notebook = gtk.Notebook()
        notebook.set_tab_pos(gtk.POS_TOP)
        
        openmalaria = NotebookFrame('')
        schemaTranslator = NotebookFrame('', False)
        notebook.append_page(openmalaria, gtk.Label('openMalaria'))
        notebook.append_page(schemaTranslator, gtk.Label('schemaTranslator'))
        
        openmalaria.add_import_button()
        #openmalaria.add_multiple_scenarios_button()
        openmalaria.add_terminal()
        openmalaria.add_start_button()
        openmalaria.add_popSize_entry()
        openmalaria.add_stop_button()
        
        openmalaria.add_option_button('Use Livegraph', '--liveGraph')
        openmalaria.add_option_button('Checkpointing', '-- --checkpoint')
        openmalaria.add_option_button("Don't cleanup", '-c')
        
        #window2 = ScenariosChoice()
        #window2.show()
        
        
        '''
            second part: schemaTranslator
        '''
        
        schemaTranslator.add_import_button()
        schemaTranslator.add_terminal()
        schemaTranslator.add_start_button(True,0,2,"Start translation", False)
        
        #schemaTranslator.add_option_button('')
        
        #add the objects to the window
        self.window.add(notebook)
        
        #show the objects
        #sim_label.show()
        openmalaria.show()
        schemaTranslator.show()
        notebook.show()
        
        #show the window
        self.window.show()
        
    def main(self):
        gtk.main()
    
if __name__ == "__main__":
    omfrontend = OMFrontend()
    omfrontend.main()
        
