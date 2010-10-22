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
import gobject

import fnmatch
import string
import re
import tempfile
import time
import os
import exceptions
import shutil
import signal


from FileViewersContainerDialog import FileViewersContainer
from ..tools_management.JavaAppsRun import SchemaTranslatorRun

'''
This Frame lists the xml files. This list allows the user to do 
batch jobs without freezing the whole GUI'''        
class FileList(gtk.Frame):
    def __init__(self, parent = None, experimentDialog = False, notebookFrame = None):
        gtk.Frame.__init__(self)
        self.set_label('Scenarios')
        
        self.notebookFrame = notebookFrame
        self.scrolledWindow = gtk.ScrolledWindow()
        self.scrolledWindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        
        self.experimentDialog = experimentDialog
        self.parent_window = parent
        
        self.vbox = gtk.VBox(False, 2)
        
        self.liststore = gtk.ListStore(str, str, gtk.gdk.Pixbuf, gobject.TYPE_BOOLEAN)
        self.treeview = gtk.TreeView(self.liststore)
        
        if experimentDialog:
            self.tcolumn1 = gtk.TreeViewColumn(' Reference   ')
        else:
            self.tcolumn1 = gtk.TreeViewColumn(' Selection   ')
        
        self.tcolumn2 = gtk.TreeViewColumn(' Loaded files   ')
        
        if not experimentDialog:
            self.tcolumn3 = gtk.TreeViewColumn(' Outcomes   ')
        
        self.treeview.append_column(self.tcolumn1)
        self.treeview.append_column(self.tcolumn2)
        
        if not experimentDialog:
            self.treeview.append_column(self.tcolumn3)
        
        self.cell = gtk.CellRendererToggle()
        self.cell.set_property('activatable', True)
        model = self.treeview.get_model()
        if not experimentDialog:
            self.cell.connect( 'toggled', self.cell_toggle, model)
        else:
            self.cell.connect('toggled', self.creator_cell_toggle, model)
            self.old_path = None
    
        self.tcolumn1.pack_start(self.cell, True)
        self.tcolumn1.add_attribute(self.cell, "active", 3)
        
        self.cell_text = gtk.CellRendererText()
        self.tcolumn2.pack_start(self.cell_text, True)
        self.tcolumn2.set_attributes(self.cell_text, text=1)
        
        if not experimentDialog:
            self.cell2 = gtk.CellRendererPixbuf()
            self.tcolumn3.pack_start(self.cell2, True)
            self.tcolumn3.add_attribute(self.cell2, 'pixbuf', 2)

        
        self.scrolledWindow.add_with_viewport(self.treeview)
        self.filenames = list()
        self.scrolledWindow.show_all()
        
        self.vbox.pack_start(self.scrolledWindow, True, True, 2)
        
        if experimentDialog:
            hbox = gtk.HBox(False, 2)
            comboBox = gtk.combo_box_new_text()
            comboBox.append_text('base')
            comboBox.append_text('reference')
            comboBox.append_text('comparator')
            comboBox.connect('changed', self.set_reference_type)
            comboBox.set_active(0)
            hbox.pack_start(comboBox, False, False, 2)
            self.vbox.pack_start(hbox, False, False, 2)
        
        if not experimentDialog:
            self.hbox = gtk.HBox(False, 5)
            
            self.vbox_select_all = gtk.VBox(False, 2)
            self.select_all_button = gtk.Button('Select All')
            self.select_all_button.connect('clicked', self.select_all)
            self.vbox_select_all.pack_start(self.select_all_button, False, False, 2)
            
            self.vbox_unselect_all = gtk.VBox(False, 2)
            self.unselect_all_button = gtk.Button('Unselect All')
            self.unselect_all_button.connect('clicked', self.unselect_all)
            self.vbox_unselect_all.pack_start(self.unselect_all_button, False, False, 2)
            
            self.vbox_selected = gtk.VBox(False, 2)
            self.label_selected = gtk.Label('With selected: ')
            self.vbox_selected.pack_start(self.label_selected, False, False, 2)
            
            self.vbox_edit = gtk.VBox(False, 2)
            self.edit_button = gtk.Button()
            self.edit_button.set_image(gtk.image_new_from_stock(gtk.STOCK_EDIT, gtk.ICON_SIZE_MENU))
            self.edit_button.connect('clicked', self.edit_scenarios)
            self.vbox_edit.pack_start(self.edit_button, False, False, 2)
            
            self.vbox_close = gtk.VBox(False, 2)
            self.close_button = gtk.Button()
            self.close_button.set_image(gtk.image_new_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_MENU))
            self.close_button.connect('clicked', self.close_scenarios)
            self.vbox_close.pack_start(self.close_button, False, False, 2)
            
            
            self.hbox.pack_start(self.vbox_select_all, False, False, 2)
            self.hbox.pack_start(self.vbox_unselect_all, False, False, 2)
            self.hbox.pack_start(self.vbox_selected, False, False, 2)
            self.hbox.pack_start(self.vbox_edit, False, False, 2)
            self.hbox.pack_start(self.vbox_close, False, False, 2)
            
            
            self.vbox.pack_start(self.hbox, False, False, 2)
            
            self.fileViewersContainer = FileViewersContainer(parent)
            self.filenames = list()
            
        self.total_selected = 0
        self.add(self.vbox)
        self.show_all()
                
    
    '''
    select_all:
    This function is used with the select all button.
    If the select all button is pressed, then all the
    toggled buttons in the file list will be active, and
    so all the files will be active''' 
    def select_all(self, widget):
        self.setSelectState(True)
    
    '''
    unselect_all:
    This function deactivates all the toggle buttons in the
    list'''
    def unselect_all(self, widget):
        self.setSelectState(False)
    '''
    setSelectState:
    Sets the state of all the toggle buttons in the list'''
    def setSelectState(self, state):
        iterator = self.liststore.get_iter_first()
        self.total_selected = 0
        while iterator:
            self.liststore.set_value(iterator, 3, state)
            if state:
                self.total_selected += 1
            iterator = self.liststore.iter_next(iterator)
        
        self.update_livegraph_toggle()
        
    '''
    cell_toggle:
    Changes a row's toggle button state
    If more than 1 scenarios are selected, then the livegraph
    option is deactivated'''
    def cell_toggle(self, cell, path, model):
        model[path][3] = not model[path][3]
        
        if not model[path][3]:
            self.total_selected -=1
        else:
            self.total_selected +=1
        
        self.update_livegraph_toggle()
    
    '''
    creator_cell_toggle:
    In this case, only one row at a time can be set
    to true (Select all isn't used in the experiment creator)'''
    def creator_cell_toggle(self, cell, path, model):
        if not self.old_path == None:
            model[self.old_path][3] = False
            
        model[path][3] = not model[path][3]
        self.old_path = path
    
    '''
    update_livegraph_toggle:
    Sets if the toggle button for sim_option_livegraph is sensitive.
    If there are more than two selected scenarios, then the livegraph
    option is disabled'''
    def update_livegraph_toggle(self):
        if(self.total_selected > 1):
            self.notebookFrame.sim_option_livegraph.set_sensitive(False)
            self.notebookFrame.sim_option_livegraph.set_active(False)
        else:
            self.notebookFrame.sim_option_livegraph.set_sensitive(True)
                
        
    '''
    create_icons:
    Create_icons for pixbuf columns'''
    def createIcons(self, column, cell, model, iter, col):
        stock = model.get_value(iter, col)
        pb = self.treeview.render_icon(stock, gtk.ICON_SIZE_MENU, None)
        cell.set_property('pixbuf', pb)
    
    '''
    addScenarios:
    Adds all in filenames list given files in the filelist.
    Checks scenario's schema version'''        
    def addScenarios(self, filenames, added_message = None):
        
        scenario_infos_list = list()
        
        for i in range(len(filenames)):
            actual_filename = filenames[i]
            if not(os.path.isdir(actual_filename)):
                self.filenames.append(actual_filename)
                head, tail = os.path.split(actual_filename)
                actual_name = tail
                actual_name = string.split(actual_name, '.')[0]
                scenario_infos = list()
                scenario_infos.append(actual_name)
                scenario_infos.append(actual_filename)
                scenario_infos_list.append(scenario_infos)
        
        translator = SchemaTranslatorRun()
        runnable_scenarios = translator.check_and_return_runnable_scenarios(scenario_infos_list, self.parent_window, added_message)
        
        if len(runnable_scenarios)>0 :
            for runnable_scenario in runnable_scenarios:
                self.add_file(runnable_scenario[1], runnable_scenario[0])
        elif self.experimentDialog:
            self.destroy()
            
    
    '''
    add_file:
    Adds a single file in the filelist with informations 
    about path, name, outcomes (at the beginning none) and 
    the toggle button state (False, because the file isn't selected...)'''
    def add_file(self, path, name):
        pb = self.treeview.render_icon(gtk.STOCK_REMOVE, gtk.ICON_SIZE_MENU, None)
        self.liststore.append([path, name, pb , False])
    
    '''
    close_scenarios:
    Removes all the selected scenarios (toggle button is active) from the list'''    
    def close_scenarios(self, widget):
        iterator = self.liststore.get_iter_first()
        while iterator:
            iterator_temp = self.liststore.iter_next(iterator)
            if(self.liststore.get_value(iterator, 3)== True):
                self.liststore.remove(iterator)
                self.total_selected -=1
            iterator = iterator_temp
        self.update_livegraph_toggle()
            
    
    '''
    return_first_true:
    Returns the first activated toggle button path'''
    def return_first_true(self):
        iterator = self.liststore.get_iter_first()
        first_found_path = None
        not_found = True
        while iterator and not_found:
            if(self.liststore.get_value(iterator, 3) == True):
                first_found_path = self.liststore.get_value(iterator, 0)
                not_found = False
            iterator = self.liststore.iter_next(iterator)
        return first_found_path
    
    '''
    return_sweep_list:
    Returns the actual sweep files' list'''
    def return_sweep_list(self):
        iterator = self.liststore.get_iter_first()
        sweep = list()
        path = list()
        state = list()
        sweep.append(path)
        sweep.append(state)
        while iterator:
            path.append(self.liststore.get_value(iterator, 0))
            state.append(self.liststore.get_value(iterator, 3))
            iterator = self.liststore.iter_next(iterator)
            
        return sweep
                
    
    '''
    edit_scenarios:
    Starts the editor for the selected scenarios, but a maximum of 10 to avoid
    a freeze of the GUI'''        
    def edit_scenarios(self, widget):
        iterator = self.liststore.get_iter_first()
        max_editable = False
        filenames = list()
        i = 0
        while iterator and not max_editable: 
            if i == 10:
                max_editable = True
            else:
                if(self.liststore.get_value(iterator, 3)==True):
                    filenames.append(self.liststore.get_value(iterator, 0))
                    i+=1
            iterator = self.liststore.iter_next(iterator)
        
        if len(filenames) > 0 :
            self.fileViewersContainer.removeScenarios()
            self.fileViewersContainer.addScenarios(filenames)
    
    '''
    get_selected_filenames:
    Returns the filenames, names and iterators (row number) of  
    all the selected files in the list'''      
    def get_selected_filenames(self):
        iterator = self.liststore.get_iter_first()
        selected = list()
        selected_names = list()
        selected_filenames = list()
        selected_iterators = list()
        selected.append(selected_filenames)
        selected.append(selected_names)
        selected.append(selected_iterators)
        while iterator:
            if(self.liststore.get_value(iterator, 3)==True):
                selected_filenames.append(self.liststore.get_value(iterator, 0))
                selected_names.append(self.liststore.get_value(iterator, 1))
                iterator_temp = iterator
                selected_iterators.append(iterator_temp)
            iterator = self.liststore.iter_next(iterator)
                
        return selected
    
    '''
    set_simulation_state:
    sets a success/failure icon after a scenario has been simulated in the
    scenario's row'''
    def set_simulation_state(self, state, iterator):
        if state:
            pb = self.treeview.render_icon(gtk.STOCK_APPLY, gtk.ICON_SIZE_MENU, None)
            self.liststore.set_value(iterator,2, pb)
        else:
            pb = self.treeview.render_icon(gtk.STOCK_CANCEL, gtk.ICON_SIZE_MENU, None)
            self.liststore.set_value(iterator,2, pb)
    
    '''
    reset_simulation_state:
    Before beginning a new batch/simulation, the whole success/failures 
    icons are reseted'''
    def reset_simulation_state(self):
        iterator = self.liststore.get_iter_first()
        while iterator:
            pb = self.treeview.render_icon(gtk.STOCK_REMOVE, gtk.ICON_SIZE_MENU, None)
            self.liststore.set_value(iterator,2, pb)
            iterator = self.liststore.iter_next(iterator)
            
    '''
    set_reference_type:
    Sets the actual reference_type (This could be base, comparator or reference)'''
    def set_reference_type(self, comboBox):
        self.reference_type = comboBox.get_active_text()
    '''
    get_reference_type:
    Returns the reference typ (base, comparator or reference)'''
    def get_reference_type(self):
        return self.reference_type