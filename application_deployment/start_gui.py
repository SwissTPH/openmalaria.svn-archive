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

from VirtualTerminal import VirtualTerminal


class OMFrontend:
    
    base_folder = os.getcwd()
    testSrcDir = base_folder + "/run_scenarios/scenarios_to_run"
    
    def get_scenarios_combobox(self):
        sim_cbox = gtk.combo_box_new_text()
        for filename in os.listdir(self.testSrcDir):
                if fnmatch.fnmatch(filename, "*.xml"):
                  sim_cbox.append_text(string.split(filename,"scenario")[1])
        return sim_cbox
    
    def get_popSize_entry(self):
        sim_option_popsize = gtk.Entry()
        filename = 'scenario' + self.sim_cbox.get_active_text()
        
        src=open(self.testSrcDir +'/'+ filename)
        pop_string=src.read()
        src.close()
        
        popSizeRE = re.compile('popSize="\d*"')
        popSizeString = popSizeRE.findall(pop_string)[0]
        popSizeString = popSizeString[len('popSize="'):len(popSizeString)-2]
        
        sim_option_popsize.set_text(popSizeString)
        return sim_option_popsize
    
    def update_popSize_entry(self, widget, data=None):
        filename = 'scenario' + self.sim_cbox.get_active_text()
        
        src=open(self.testSrcDir +'/'+ filename)
        pop_string=src.read()
        src.close()
        
        popSizeRE = re.compile('popSize="\d*"')
        popSizeString = popSizeRE.findall(pop_string)[0]
        popSizeString = popSizeString[len('popSize="'):len(popSizeString)-1]
        
        self.sim_option_popsize.set_text(popSizeString)
    
    def update_popSize_scenario(self, data=None):
        filename = 'scenario' + self.sim_cbox.get_active_text()
        
        src=open(self.testSrcDir +'/'+ filename)
        pop_string=src.read()
        src.close()
        
        popSizeRE = re.compile('popSize="\d*"')
        popSizeString = popSizeRE.findall(pop_string)[0]
        popSizeString = popSizeString[len('popSize="'):len(popSizeString)-1]
        
        if not(popSizeString == self.sim_option_popsize.get_text()):
            pop_string = popSizeRE.sub('popSize="'+self.sim_option_popsize.get_text()+'"', pop_string)
            dest= open(self.testSrcDir +'/'+ filename, 'w')
            dest.write(pop_string)
            dest.close()
        
        
    
    def delete_event(self, widget, event, data=None):
        return False
    
    def destroy(self, widget, data=None):
        gtk.main_quit()
        
    def importScenario(self, widget, data=None):
        imported_path = self.sim_import_button.get_filename()
        imported_split = string.split(imported_path, "/")
        imported_name = imported_split[len(imported_split)-1]
        
        src=open(imported_path)
        scen_string=src.read()
        src.close()
        
        filenames = list()
        
        for filename in os.listdir(self.testSrcDir):
            filenames.append(filename)
            
        test_filename = imported_name
        i = 1
        
        while(filenames.count(test_filename)>0):
            test_split = string.split(imported_name, '.')
            test_filename = test_split[0] + '_'+str(i)+'.'+test_split[1]
            i = i + 1
            
        imported_name = test_filename      
    
        dest= open(self.testSrcDir+'/'+imported_name, 'w')
        dest.write(scen_string)
        dest.close()
        
        self.sim_cbox.append_text(string.split(imported_name, "scenario")[1])
        
    def openMalariaCommand(self, widget, data=None):
        
        self.update_popSize_scenario()
        
        command = './run.py '
        
        command = command + string.split(self.sim_cbox.get_active_text(), '.')[0]
        
        if(self.sim_option_livegraph.get_active()):
            command = command + ' -l'
        if(self.sim_option_nocleanup.get_active()):
            command = command + ' -c'
        if(self.sim_option_checkpoint.get_active()):
            command = command + ' -- --checkpoint'
            
        self.terminal.run_command(command)
        
        
    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect("delete_event", self.delete_event)
        self.window.connect("destroy", self.destroy)
        self.window.set_border_width(10)
        
        #notebook
        notebook = gtk.Notebook()
        notebook.set_tab_pos(gtk.POS_TOP)
        
        openmalaria_label = gtk.Label('openMalaria')
        openmalaria_frame = gtk.Frame('')
        
        schematranslator_label = gtk.Label('schemaTranslator')
        schematranslator_frame = gtk.Frame('')
        
        notebook.append_page(openmalaria_frame, openmalaria_label)
        notebook.append_page(schematranslator_frame, schematranslator_label)
        
        #boxes for simulator
        v_sim_box = gtk.VBox(False, 10)
        h_sim_box = gtk.HBox(False, 20)
        
        ''' 
            first part: openMalaria simulator
        '''
        
        #Scenario
        first_line_box = gtk.HBox(False, 5)
        
        sim_cbox_vbox = gtk.VBox(False, 2)
        sim_cbox_label = gtk.Label('Scenario')
        sim_cbox_label.set_alignment(0,0) 
        self.sim_cbox = self.get_scenarios_combobox()
        self.sim_cbox.set_active(0)
        sim_cbox_vbox.pack_start(sim_cbox_label, False, False, 2)
        sim_cbox_vbox.pack_start(self.sim_cbox, False, False, 2)
        
        sim_import_vbox = gtk.VBox(False,2)
        sim_import_label = gtk.Label('Import scenario')
        self.sim_import_button = gtk.FileChooserButton('Import...')
        self.sim_import_button.connect('file-set', self.importScenario)
        sim_import_vbox.pack_start(sim_import_label, False, False, 2)
        sim_import_vbox.pack_start(self.sim_import_button, False, False, 2)
        
        first_line_box.pack_start(sim_import_vbox, False, False, 10)
        first_line_box.pack_start(sim_cbox_vbox, False, False, 2)
        
        #Options
        
        sim_option_vbox4 = gtk.VBox(False, 2)
        sim_option_label4 = gtk.Label("Population Size")
        sim_option_label4.set_alignment(0,0)
        self.sim_option_popsize = self.get_popSize_entry()
        self.sim_cbox.connect('changed',self.update_popSize_entry)
        sim_option_vbox4.pack_start(sim_option_label4, False, False, 2)
        sim_option_vbox4.pack_start(self.sim_option_popsize, False, False, 2)
        
        sim_option_vbox1 = gtk.VBox(False, 2)
        sim_option_label = gtk.Label("Options")
        sim_option_label.set_alignment(0,0)
        self.sim_option_livegraph = gtk.CheckButton("Use Livegraph", False)
        sim_option_vbox1.pack_start(sim_option_label, False, False, 2)
        sim_option_vbox1.pack_start(self.sim_option_livegraph, False, False, 2)
        
        sim_option_vbox2 = gtk.VBox(False, 2)
        sim_option_label2 = gtk.Label("")
        sim_option_label2.set_alignment(0,0)
        self.sim_option_checkpoint = gtk.CheckButton("Checkpointing", False)
        sim_option_vbox2.pack_start(sim_option_label2, False, False, 2)
        sim_option_vbox2.pack_start(self.sim_option_checkpoint, False, False, 2)
        
        sim_option_vbox3 = gtk.VBox(False, 2)
        sim_option_label3 = gtk.Label("")
        sim_option_label3.set_alignment(0,0)
        self.sim_option_nocleanup = gtk.CheckButton("Don't cleanup", False)
        sim_option_vbox3.pack_start(sim_option_label3, False, False, 2)
        sim_option_vbox3.pack_start(self.sim_option_nocleanup, False, False, 2)
        
        first_line_box.pack_start(sim_option_vbox4, False, False, 2)
        first_line_box.pack_start(sim_option_vbox1, False, False, 2)
        first_line_box.pack_start(sim_option_vbox2, False, False, 2)
        first_line_box.pack_start(sim_option_vbox3, False, False, 2)
        
        
        v_sim_box.pack_start(first_line_box, False, False, 0)
        
        #terminal output
        self.terminal = VirtualTerminal()
        terminal_start_button = gtk.Button("Start simulation")
        terminal_start_button.connect('clicked', self.openMalariaCommand) 
        terminal_option_box = gtk.VBox(False, 2)
        terminal_option_box.pack_start(self.terminal, True, True, 0)
        terminal_option_box.pack_start(terminal_start_button, False, False, 0)
        h_sim_box.pack_start(terminal_option_box, True, True,0)
        
        
        #create import scenario button
        #self.button_import = gtk.Button("Import...")
        #import_scenario button actions
        #self.button_import.connect("clicked", self.importScenario, None)
        #self.button_import.connect_object("clicked", gtk.Widget.destroy, self.window)
        v_sim_box.pack_start(h_sim_box, False, False,0)
        
        #add the objetcts to the frames
        openmalaria_frame.add(v_sim_box)
        
        '''
            second part: schemaTranslator
        '''
        
        
        #add the objects to the window
        self.window.add(notebook)
        
        #show the objects
        #sim_label.show()
        first_line_box.show()
        self.sim_cbox.show()
        sim_cbox_label.show()
        sim_cbox_vbox.show()
        self.sim_import_button.show()
        sim_import_label.show()
        sim_import_vbox.show()
        sim_option_label.show()
        sim_option_label2.show()
        sim_option_label3.show()
        sim_option_label4.show()
        self.sim_option_livegraph.show()
        self.sim_option_checkpoint.show()
        self.sim_option_nocleanup.show()
        self.sim_option_popsize.show()
        sim_option_vbox1.show()
        sim_option_vbox2.show()
        sim_option_vbox3.show()
        sim_option_vbox4.show()
        self.terminal.show()
        terminal_start_button.show()
        terminal_option_box.show()
        v_sim_box.show()
        h_sim_box.show()
        openmalaria_label.show()
        openmalaria_frame.show()
        schematranslator_label.show()
        schematranslator_frame.show()
        notebook.show()
        
        #show the window
        self.window.show()
        
    def main(self):
        gtk.main()
    
if __name__ == "__main__":
    omfrontend = OMFrontend()
    omfrontend.main()
        
