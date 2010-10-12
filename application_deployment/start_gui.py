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
import fnmatch
import string
import re
import tempfile
import gobject
import time
import os
import exceptions
import shutil
import signal

from xml.dom.minidom import parse
from xml.dom.minidom import Node

#from VirtualTerminal import VirtualTerminal
from VirtualTerminal_win import VirtualTerminal_win
from OpenMalariaRun import OpenMalariaRun
from JavaAppsRun import SchemaTranslatorRun
from JavaAppsRun import LiveGraphRun
from JavaAppsRun import ExperimentCreatorRun


'''
This Frame shows all the outputs' folders created during
the session'''
class ActualScenariosFolders(gtk.Frame):
    
    def __init__(self):
        
        gtk.Frame.__init__(self)
        self.set_border_width(10)
        self.set_label('Outputs')
        
        self.liststore = gtk.ListStore(str, str, str)
        self.treeview = gtk.TreeView(self.liststore)
        self.treeview.connect('button-press-event', self.double_click)
        
        self.tcolumn1 = gtk.TreeViewColumn('  ')
        self.tcolumn2 = gtk.TreeViewColumn('  name  ')
        self.tcolumn3 = gtk.TreeViewColumn('  path  ')
        
        self.treeview.append_column(self.tcolumn1)
        self.treeview.append_column(self.tcolumn2)
        self.treeview.append_column(self.tcolumn3)
        
        self.cell = gtk.CellRendererPixbuf()
        self.cell_name = gtk.CellRendererText()
        self.cell_path = gtk.CellRendererText()
        
        self.tcolumn1.pack_start(self.cell, True)
        self.tcolumn1.set_cell_data_func(self.cell, self.createIcons)
        
        self.tcolumn2.pack_start(self.cell_name, True)
        self.tcolumn2.set_attributes(self.cell_name, text=2)
        
        self.tcolumn3.pack_start(self.cell_path, True)
        self.tcolumn3.set_attributes(self.cell_path, text=0)
        
        self.scrolledWindow = gtk.ScrolledWindow()
        self.scrolledWindow.add_with_viewport(self.treeview)
        self.scrolledWindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.First = True

        self.add(self.scrolledWindow)
        self.show_all()
    
    '''
    createIcons:
    Adds a folder Icon in the treelist for each output's folder''' 
    def createIcons(self, column, cell, model, iter):
        stock = model.get_value(iter, 1)
        pb = self.treeview.render_icon(stock, gtk.ICON_SIZE_MENU, None)
        cell.set_property('pixbuf', pb)
        if(self.First):
            self.show()
            self.First = False
            
    '''
    double_click:
    Opens an explorer view, so the user can look at the outputs'''
    def double_click(self, widget, event, data=None):
        if(event.type == gtk.gdk._2BUTTON_PRESS):
            path = self.treeview.get_path_at_pos(int(event.x), int(event.y))
            iter = self.liststore.get_iter(path[0])
            folder_path = self.liststore.get(iter, 0)[0]
            
            if sys.platform == 'win32':
                os.startfile(folder_path)
            elif sys.platform == 'darwin':
                os.system('open "%s"' % folder_path)
            else:
                os.system('xdg-open "%s"' % folder_path)
    '''
    add_folder:
    Adds a new outputs' folder in the list'''           
    def add_folder(self, path, name):
        self.liststore.append([path, gtk.STOCK_DIRECTORY, name])
        self.show()
'''
This Frame lists the xml files. This list allows the user to do 
batch jobs without freezing the whole GUI'''        
class FileList(gtk.Frame):
    
    IS_USING_CORRECT_SCENARIO_VERSION = 0
    IS_TRANSLATABLE = 1
    IS_NOT_TRANSLATABLE = -1
    NOT_FOUND = -2
    
    def __init__(self, parent = None, experimentDialog = False):
        gtk.Frame.__init__(self)
        self.set_label('Scenarios')
        
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
    check_scenario_version:
    checks whether or not the loaded scenario schema version is supported
    by the openmalaria application. If the schema version is higher than
    the one used by the openmalaria application, then this schema can't be used
    at all and no translation is possible. On an other hand, if the schema version
    is lower than the one used by the openmalaria application, then in some cases,
    a translation is possible.'''
    def check_scenario_version(self, scenario_path):
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
                    print schema_vers
                    if schema_vers > int(OpenMalariaRun.actual_scenario_version):
                        return self.IS_NOT_TRANSLATABLE
                    elif schema_vers < int(OpenMalariaRun.actual_scenario_version):
                        return self.IS_TRANSLATABLE
                    else:
                        return self.IS_USING_CORRECT_SCENARIO_VERSION   
                except exceptions.ValueError:
                    return self.IS_NOT_TRANSLATABLE
        else:
            return self.NOT_FOUND
                
    
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
            NotebookFrame.sim_option_livegraph.set_sensitive(False)
            NotebookFrame.sim_option_livegraph.set_active(False)
        else:
            NotebookFrame.sim_option_livegraph.set_sensitive(True)
                
        
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
    def addScenarios(self, filenames):
        wrong_version_not_translatable_scenarios = list()
        wrong_version_translatable_scenarios = list()
        not_found_scenarios = list()
        
        for i in range(len(filenames)):
            actual_filename = filenames[i]
            if not(os.path.isdir(actual_filename)):
                self.filenames.append(actual_filename)
                head, tail = os.path.split(actual_filename)
                actual_name = tail
                actual_name = string.split(actual_name, '.')[0]
                if not self.experimentDialog:
                    scenario_infos = list()
                    scenario_infos.append(actual_name)
                    scenario_infos.append(actual_filename)
                    scenario_check = self.check_scenario_version(actual_filename)
                    if(scenario_check == self.IS_USING_CORRECT_SCENARIO_VERSION):
                        self.add_file(actual_filename, actual_name)
                    elif(scenario_check == self.IS_TRANSLATABLE):
                        wrong_version_translatable_scenarios.append(scenario_infos)
                    elif(scenario_check == self.IS_NOT_TRANSLATABLE):
                        wrong_version_not_translatable_scenarios.append(scenario_infos)
                    else:
                        not_found_scenarios.append(scenario_infos)
                else:
                    self.add_file(actual_filename, actual_name)
                    
        if len(wrong_version_translatable_scenarios) > 0 or len(wrong_version_not_translatable_scenarios) > 0 or len(not_found_scenarios) > 0:
            self.show_import_problems_message(wrong_version_not_translatable_scenarios, wrong_version_translatable_scenarios, not_found_scenarios)
            
    '''
    show_import_problems_message:
    Shows the found problems during the importation of some scenarios in openMalariaTools'''
    def show_import_problems_message(self, wvnts, wvts, nfs):
        
        if len(wvts) > 0:
            problems = str(len(wvts)) + " scenarios are using an older (possibly translatable) schema version. Would you like that the system tries to update the scenarios using an older schema version? "
            import_problems_message = gtk.MessageDialog(self.parent_window, gtk.DIALOG_MODAL,gtk.MESSAGE_WARNING,gtk.BUTTONS_NONE, problems)
            import_problems_message.add_button('Yes', gtk.RESPONSE_YES)
            import_problems_message.add_button('No', gtk.RESPONSE_NO)
            import_problems_message.connect('response', self.start_translator, wvts)
            import_problems_message.run()
            import_problems_message.destroy()
            
        if len(wvnts)>0:
            error_message = str(len(wvnts)) + " scenarios are using an unsupported schema version. Please try to update to a newest version of openmalariaTools..."
            import_error_message = gtk.MessageDialog(self.parent_window, gtk.DIALOG_MODAL,gtk.MESSAGE_ERROR,gtk.BUTTONS_NONE, problems)
            import_error_message.add_button('Ok', gtk.RESPONSE_OK)
            import_error_message.run()
            import_error_message.destroy()     
    
    '''
    start_translator:
    Starts the translator if the user press ok on the message dialog'''
    def start_translator(self, dialog, response_id, wvts):
        if response_id == gtk.RESPONSE_YES:
            print 'fais chier bordel de merde!'
            progress_bar = gtk.ProgressBar()
            progress_bar.set_text("Scenarios' translation...")
            dialog.vbox.pack_start(progress_bar, True, True, 2)
            dialog.vbox.show_all()
            div = len(wvts)
            translator = SchemaTranslatorRun()
            i=1
            for scenario_to_translate in wvts:
                output_folder = translator.start_schematranslator_run_single(scenario_to_translate[1])
                output_file_path = os.path.join(output_folder, scenario_to_translate[0]+'.xml')
                if os.path.exists(output_file_path):
                    self.add_file(output_file_path, scenario_to_translate[0])
                progress_bar.set_fraction(i/div)
                i +=1
                       
    
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
            iterator = iterator_temp
    
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
                                
'''
FileViewersContainers(gtk.Window):
Window containing all the loaded scenarios.
Every scenario will be added in a notebook.
'''
class FileViewersContainer(gtk.Dialog):
    
    
    def __init__(self, parent):
        gtk.Dialog.__init__(self, 'Viewer', parent, 0, None)
        
        if parent != None:
            self.resize(400, 500)
        
        
        self.set_border_width(10)
        self.notebook = gtk.Notebook()
        self.notebook.set_tab_pos(gtk.POS_TOP)
        self.connect('delete-event', self.nothing)
        self.vbox.pack_start(self.notebook, True, True, 2)
        self.show_all()
        self.filenames = list()
        self.names = list()
        
        icon_path = os.path.join(os.getcwd(), 'application', 'common', 'om.ico')
        self.set_icon_from_file(icon_path)
        
        self.hide()
        
    '''
    create_tab_label:
    create a tab_label with an icon for closing the tab'''    
    def create_tab_label(self, title, actual_fileViewer):
        box = gtk.HBox(False, 0)
        label = gtk.Label(title)
        box.pack_start(label)
        
        close_image = gtk.image_new_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_MENU)
        image_w, image_h = gtk.icon_size_lookup(gtk.ICON_SIZE_MENU)

        close = gtk.Button()
        close.set_relief(gtk.RELIEF_NONE)
        close.set_focus_on_click(False)
        close.add(close_image)
        box.pack_start(close, False, False)
        
        style = gtk.RcStyle()
        style.xthickness = 0
        style.ythickness = 0
        close.modify_style(style)

        box.show_all()
        
        close.connect('clicked', self.removeScenario, label, actual_fileViewer)
        
        return box
    
    '''
    addScenarios:
    Add new scenarios in the container and set the filenames'''    
    def addScenarios(self, filenames):
        
        if(len(filenames)>0):
            self.show()
            
        for i in range(len(filenames)):
            actual_filename = filenames[i]
            if not(os.path.isdir(actual_filename)):
                self.filenames.append(actual_filename)
                head, tail = os.path.split(actual_filename)
                actual_name = tail
                actual_name = string.split(actual_name, '.')[0]
                self.names.append(actual_name)
                actual_fileViewer = FileViewer('')
                actual_fileViewer.parseFile(actual_filename, actual_name)
                label = self.create_tab_label(actual_name, actual_fileViewer)
                self.notebook.insert_page(actual_fileViewer, label)
                
    '''
    removeScenarios:
    Before a new load, the actual "fileviewers" are removed from the notebook'''    
    def removeScenarios(self):
        for i in range(self.notebook.get_n_pages()):
            self.notebook.remove_page(0)
        if(self.notebook.get_n_pages()==0):
            self.hide()
            
    '''
    removeScenario:
    Removes a single scenario from the FileViewersContainer object'''
    def removeScenario(self, sender, widget, data=None):
        page = self.notebook.page_num(data)
        self.notebook.remove_page(page)
        # Need to refresh the widget -- 
        # This forces the widget to redraw itself.
        self.notebook.queue_draw_area(0,0,-1,-1)
        self.updateFilenames()
        if(self.notebook.get_n_pages()==0):
            self.hide()
            
    '''
    updateFilenames:
    Update the actual names on the fileViewersContainer object'''        
    def updateFilenames(self):
        only_files = list()
        only_files_names = list()
        for i in range(self.notebook.get_n_pages()):
            fileViewer = self.notebook.get_nth_page(i)
            only_files.append(fileViewer.actual_path)
            only_files_names.append(fileViewer.actual_name)
        self.filenames = only_files
        self.names = only_files_names
    
    '''
    hasContent:
    Checks if there is some content (scenarios) displayed''' 
    def hasContent(self):
        return len(self.names)>0
                
    '''
    nothing:
    This function is there to avoid that the user kill the 
    current FileViewersContainer object. In fact, the object
    will just be hidden'''        
    def nothing(self, widget, data=None):
        self.hide()
        return True
        
'''
The FileViewer allows the user to see the scenarios
as a tree representation.'''
class FileViewer(gtk.Frame):
    
    COL_NODE_NAME = 0
    COL_NODE_VALUE = 1
    COL_NODE_TYPE = 2
    COL_NODE_OBJECT = 3
    
    ELEMENT_NODE = 0
    ATTRIBUTE_NODE = 1
    
    def __init__(self, frame_name):
        gtk.Frame.__init__(self, frame_name)
        self.set_border_width(10)
        self.treestore = gtk.TreeStore(str, str, int, object)
        
        self.tree = gtk.TreeView(self.treestore)
        self.tree.set_headers_visible(False)
        self.scrolledWindow = gtk.ScrolledWindow()
        self.scrolledWindow.add_with_viewport(self.tree)
        self.scrolledWindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        
        self.tcolumn = gtk.TreeViewColumn()
        
        self.cell = gtk.CellRendererText()
        self.tcolumn.pack_start(self.cell, True)
        self.tcolumn.add_attribute(self.cell, "text", self.COL_NODE_NAME)
        
        self.cell_value = gtk.CellRendererText()
        self.tcolumn.pack_start(self.cell_value, True)
        self.tcolumn.add_attribute(self.cell_value,"text", self.COL_NODE_VALUE)
        
        self.tcolumn.set_cell_data_func(self.cell, self.nameCellDataFunc, None)
        self.tcolumn.set_cell_data_func(self.cell_value, self.valuesCellDataFunc, None)
        
        self.cell_value.connect('edited', self.updateCell)
        
        self.tree.append_column(self.tcolumn)
        self.add(self.scrolledWindow)
        
        self.tree.show()
        self.scrolledWindow.show()
        self.show()
        self.is_stopped = False

    '''
    valuesCellDataFunc: set cell_value renderer's properties.
    If a node hasn't got any value, then the associated cell isn't editable.
    Otherwise the cell is editable.
    '''
    def valuesCellDataFunc(self, column, renderer, model , iter, data):
        node_value = model.get_value(iter, self.COL_NODE_VALUE)
        if(node_value == None):
            self.cell_value.set_property('editable', False)
        else:
            self.cell_value.set_property('editable', True)
            self.cell_value.set_property('foreground', 'blue')
    
    '''
    updateCell:
    write the changes in the scenario file. If you edit a cell, then it'
    s written in the corresponding scenario file.
    '''
    def updateCell(self, cell_renderer, path, new_value, data=None):
        if not(path == None):
            iter = self.treestore.get_iter(path)
            self.treestore.set(iter, self.COL_NODE_VALUE, new_value)
            dom_node = self.treestore.get(iter, self.COL_NODE_OBJECT)[0]
            dom_node.nodeValue = self.treestore.get(iter, self.COL_NODE_VALUE)[0]
            
            dest= open(self.actual_path, 'w')
            self.dom.writexml(dest)
    
    '''
    nameCellDataFunc:
    set node type specific foreground colors
    '''
    def nameCellDataFunc(self, column, renderer, model, iter, data):
        node_type = model.get_value(iter, self.COL_NODE_TYPE)
        self.cell.set_property('editable', False)
        if (node_type == self.ELEMENT_NODE):   
            self.cell.set_property('foreground',gtk.gdk.Color(red=26985, green=35723, blue=26985))
        else:
            self.cell.set_property('foreground', gtk.gdk.Color(red=53739, green=26985, blue=51657))
        
    '''
    parseFile:
    The scenario file is parsed to create the tree representation.
    ParseFile is the initialization function. This function is followed
    by parseFileRec which does a depth-first recursion on every nodes
    '''    
    def parseFile(self, file_path, scenario_name):
        self.actual_path = file_path
        self.actual_name = scenario_name
        self.tcolumn.set_title('')
        self.treestore.clear()
        self.dom = parse(file_path)
        root = self.dom.getElementsByTagName("scenario")[0]
        root_tree = self.treestore.append(None)
        if(root.hasAttributes()):
            self.treestore.set(root_tree, 
                         self.COL_NODE_NAME, '< '+root.nodeName,
                         self.COL_NODE_VALUE, None,
                         self.COL_NODE_TYPE, self.ELEMENT_NODE,
                         self.COL_NODE_OBJECT, root)
        else:
            self.treestore.set(root_tree, 
                         self.COL_NODE_NAME, '< '+root.nodeName + ' >',
                         self.COL_NODE_VALUE, None,
                         self.COL_NODE_TYPE, self.ELEMENT_NODE,
                         self.COL_NODE_OBJECT, root)
            
        if root.hasAttributes():
                attributes = root.attributes
                for i in range(len(attributes)):
                    attr_node = self.treestore.append(None)
                    self.treestore.set(attr_node, 
                     self.COL_NODE_NAME, attributes.item(i).nodeName, 
                     self.COL_NODE_VALUE, attributes.item(i).nodeValue,
                     self.COL_NODE_TYPE, self.ATTRIBUTE_NODE,
                     self.COL_NODE_OBJECT, attributes.item(i))
                ending_node = self.treestore.append(None)
                self.treestore.set(ending_node,
                                   self.COL_NODE_NAME, '>',
                                   self.COL_NODE_VALUE, None,
                                   self.COL_NODE_TYPE, self.ELEMENT_NODE,
                                   self.COL_NODE_OBJECT, None)
        
        children = root.childNodes
        self.parseFileRec(children, None)
        
        element_ending = self.treestore.append(None)
        self.treestore.set(element_ending,
                           self.COL_NODE_NAME, '</ '+root.nodeName+' >',
                           self.COL_NODE_VALUE, None,
                           self.COL_NODE_TYPE, self.ELEMENT_NODE,
                           self.COL_NODE_OBJECT, None)
    
    '''
    parseFileRec:
    Recursive dom children nodes parsing'''           
    def parseFileRec(self, children, tree_node):
        allchildren = list()
        for child in children:
            if(child.nodeType == Node.ELEMENT_NODE):
                nodeValue = None
                if(child.hasChildNodes() and child.childNodes[0].nodeType == Node.TEXT_NODE):
                    nodeValue = child.childNodes[0].nodeValue
                new_node = self.treestore.append(tree_node)
                
                if(child.hasAttributes()):
                    self.treestore.set(new_node, 
                             self.COL_NODE_NAME, '< '+child.nodeName,
                             self.COL_NODE_VALUE, nodeValue,
                             self.COL_NODE_TYPE, self.ELEMENT_NODE,
                             self.COL_NODE_OBJECT, child)
                elif(child.hasChildNodes()):
                   self.treestore.set(new_node, 
                             self.COL_NODE_NAME, '< '+child.nodeName + ' >',
                             self.COL_NODE_VALUE, nodeValue,
                             self.COL_NODE_TYPE, self.ELEMENT_NODE,
                             self.COL_NODE_OBJECT, child) 
                else:
                    self.treestore.set(new_node, 
                             self.COL_NODE_NAME, '< '+child.nodeName + ' />',
                             self.COL_NODE_VALUE, nodeValue,
                             self.COL_NODE_TYPE, self.ELEMENT_NODE,
                             self.COL_NODE_OBJECT, child)  
                
                if child.hasAttributes():
                    attributes = child.attributes
                    for i in range(len(attributes)):
                        attr_node = self.treestore.append(new_node)
                        self.treestore.set(attr_node, 
                         self.COL_NODE_NAME, attributes.item(i).nodeName, 
                         self.COL_NODE_VALUE, attributes.item(i).nodeValue,
                         self.COL_NODE_TYPE, self.ATTRIBUTE_NODE,
                         self.COL_NODE_OBJECT, attributes.item(i))
                    ending_node = self.treestore.append(new_node)
                    
                    if(child.hasChildNodes()):
                        self.treestore.set(ending_node,
                                           self.COL_NODE_NAME, '>',
                                           self.COL_NODE_VALUE, None,
                                           self.COL_NODE_TYPE, self.ELEMENT_NODE,
                                           self.COL_NODE_OBJECT, None)
                    else:
                        self.treestore.set(ending_node,
                                           self.COL_NODE_NAME, '/>',
                                           self.COL_NODE_VALUE, None,
                                           self.COL_NODE_TYPE, self.ELEMENT_NODE,
                                           self.COL_NODE_OBJECT, None)
                        
                    
                if child.hasChildNodes():
                    self.parseFileRec(child.childNodes, new_node)  
                    element_ending = self.treestore.append(new_node)
                    self.treestore.set(element_ending,
                                       self.COL_NODE_NAME, '</ '+child.nodeName+' >',
                                       self.COL_NODE_VALUE, None,
                                       self.COL_NODE_TYPE, self.ELEMENT_NODE,
                                       self.COL_NODE_OBJECT, None)
             
'''
A specific FileChooserDialog:
One or more scenario files are selected, then those are loaded in the fileviewer container as trees
The FileChooserDialog is then closed.
'''
class ScenariosChoice(gtk.FileChooserDialog):
    def __init__(self, fileList, parent):
        gtk.FileChooserDialog.__init__(self, 'Scenarios to run...', parent, gtk.FILE_CHOOSER_ACTION_OPEN, ('load',gtk.RESPONSE_OK))
        icon_path = os.path.join(os.getcwd(), 'application', 'common', 'om.ico')
        self.set_icon_from_file(icon_path)
        
        self.set_border_width(10)
        self.set_select_multiple(True)
        
        base_folder = os.getcwd()
        self.run_scenarios_base = os.path.join(base_folder, 'run_scenarios', 'scenarios_to_run')
        self.set_current_folder(self.run_scenarios_base)
        
        self.fileList= fileList
        self.connect('response', self.updateFileList)
        self.connect('destroy', self.closed_scenarios_choice)
        
        filter = gtk.FileFilter()
        filter.set_name("Xml files")
        filter.add_pattern("*.xml")
        self.add_filter(filter)
        
        self.show_all()
        
    def closed_scenarios_choice(self, widget, data=None):
        NotebookFrame.load_allready_open = False
    
    '''
    updateFileViewerContainer:
    update the FileViewerContainer when new scenarios are selected
    and the load button has been clicked.
    '''
    def updateFileList(self, widget, data=None):
        scenarios = self.importScenarios()
        self.fileList.addScenarios(scenarios)
        self.destroy()
    
    '''
    importScenarios:
    if the scenarios aren't in the working directory yet, they
    are imported in the working directory
    '''
    def importScenarios(self,data=None):
        selectedFiles = self.get_filenames()
        selectedFolder = self.get_current_folder()
        if not (selectedFolder == self.run_scenarios_base):
            for i in range(len(selectedFiles)):
                selectedFiles[i] = self.importScenario(selectedFiles[i])
                print selectedFiles[i]
        return selectedFiles
    
    '''
    importScenario:
    if the scenario isn't in the working directory yet, he
    is imported in the working directory
    '''        
    def importScenario(self, path=None):
        imported_path = path
        head, tail = os.path.split(path)
        imported_name = tail
        
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
    
        dest= open(os.path.join(self.run_scenarios_base,imported_name), 'w')
        dest.write(scen_string)
        dest.close()
        
        return os.path.join(self.run_scenarios_base, imported_name)

'''
ExperimentCreatorDialog:
This gtk.Dialog allows the user to create
a full experiment (With sweeps and arms)'''    
class ExperimentCreatorDialog(gtk.Dialog):
    
    def __init__(self, mainFileList, parent):
        gtk.Dialog.__init__(self,'Experiment creation', parent,0,('Cancel', gtk.RESPONSE_REJECT,
                      'Ok', gtk.RESPONSE_ACCEPT))
        
        icon_path = os.path.join(os.getcwd(), 'application', 'common', 'om.ico')
        self.set_icon_from_file(icon_path)
        self.mainFileList = mainFileList
        
        
        hbox_name_entry= gtk.HBox(False, 2)
        name_label = gtk.Label('Experiment name ')
        self.name_entry = gtk.Entry()
        hbox_name_entry.pack_start(name_label, False, False, 1)
        hbox_name_entry.pack_start(self.name_entry, False, False, 0)
        self.vbox.pack_start(hbox_name_entry, False, False, 2)
        
        hbox_base_button = gtk.HBox(False, 2)
        base_button = gtk.Button('Select Base file')
        base_button.connect('clicked', self.open_base_file_chooser)
        self.base_entry = gtk.Entry()
        self.base_entry.set_width_chars(100)
        self.base_entry.set_sensitive(False)
        sweeps_button = gtk.Button('Add sweeps...')
        sweeps_button.connect('clicked', self.open_sweep_folder_chooser)
        hbox_base_button.pack_start(base_button, False, False, 2)
        hbox_base_button.pack_start(self.base_entry, True, True, 2)
        hbox_base_button.pack_start(sweeps_button, False, False, 2)
        
        self.vbox.pack_start(hbox_base_button, False, False, 2)
        
        hbox_options = gtk.HBox(False, 2)
        
        vbox_1 = gtk.VBox(False, 2)
        label_options = gtk.Label('Options')
        label_options.set_alignment(0,0)
        self.validate_checkbox = gtk.CheckButton('Validate', False)
        vbox_1.pack_start(label_options, False, False, 2)
        vbox_1.pack_start(self.validate_checkbox, False, False, 2)
        
        vbox_2 = gtk.VBox(False, 2)
        label_seeds = gtk.Label('')
        label_seeds.set_alignment(0,0)
        self.seeds_checkbox = gtk.CheckButton('Add Seeds')
        self.seeds_checkbox.connect('toggled', self.show_seeds_entry)
        vbox_2.pack_start(label_seeds, False, False, 2)
        vbox_2.pack_start(self.seeds_checkbox, False, False, 2)
        
        '''vbox_3 = gtk.VBox(False, 2)
        label_sql = gtk.Label('')
        label_sql.set_alignment(0,0)
        self.sql_checkbox = gtk.CheckButton('Export to database', False)
        self.sql_checkbox.connect('toggled', self.show_db_entries)
        vbox_3.pack_start(label_sql, False, False, 2)
        vbox_3.pack_start(self.sql_checkbox, False, False, 2)'''
        
        
        hbox_options.pack_start(vbox_1, False, False, 2)
        hbox_options.pack_start(vbox_2, False, False, 2)
        #hbox_options.pack_start(vbox_3, False, False, 20)
        
        
        self.vbox.pack_start(hbox_options, False, False, 2)
        
        hbox_entries = gtk.HBox(False, 2)
        
        label_nothing = gtk.Label('')
        
        
        self.vbox_seeds = gtk.VBox(False, 2)
        label_seeds = gtk.Label('Number of seeds')
        self.seeds_entry = gtk.Entry()
        self.seeds_entry.set_width_chars(10)
        self.vbox_seeds.pack_start(label_seeds, False, False, 2)
        self.vbox_seeds.pack_start(self.seeds_entry, False, False, 2)
        
        self.vbox_login = gtk.VBox(False, 2)
        label_login = gtk.Label('Login')
        label_login.set_alignment(0,0)
        self.entry_login = gtk.Entry()
        self.vbox_login.pack_start(label_login, False, False, 2)
        self.vbox_login.pack_start(self.entry_login, False, False, 2)
        
        self.vbox_passwd = gtk.VBox(False, 2)
        label_passwd = gtk.Label('Password')
        label_passwd.set_alignment(0,0)
        self.entry_passwd = gtk.Entry()
        self.vbox_passwd.pack_start(label_passwd, False, False, 2)
        self.vbox_passwd.pack_start(self.entry_passwd, False, False, 2)
        
        self.vbox_address = gtk.VBox(False, 2)
        label_server= gtk.Label('Server Address')
        label_server.set_alignment(0,0)
        self.entry_server = gtk.Entry()
        self.vbox_address.pack_start(label_server, False, False, 2)
        self.vbox_address.pack_start(self.entry_server, False, False, 2)
        
        
        hbox_entries.pack_start(label_nothing, False, False, 33)
        hbox_entries.pack_start(self.vbox_seeds, False, False, 2)
        #hbox_entries.pack_start(self.vbox_login, False, False, 13)
        #hbox_entries.pack_start(self.vbox_passwd, False, False, 13)
        #hbox_entries.pack_start(self.vbox_address, False, False, 13)
        
        self.vbox.pack_start(hbox_entries, False, False, 2)
        
        self.sweeps_notebook = gtk.Notebook()
        self.sweeps_notebook.set_tab_pos(gtk.POS_TOP)
        self.vbox.pack_start(self.sweeps_notebook, True, True, 2)
        
        self.status_label = gtk.Label('')
        self.status_label.set_alignment(0,0)
        self.vbox.pack_start(self.status_label, False, False, 2)
        self.connect('response', self.choose_action)
        self.connect('destroy', self.closed_creator)
        
        self.sweeps_paths = list()
        self.base_file_path = None
        
        self.sweep_folder_chooser_opened=False
        self.base_file_chooser_opened=False
    
        self.show_all()
        self.vbox_seeds.set_sensitive(False)
        self.vbox_login.set_sensitive(False)
        self.vbox_passwd.set_sensitive(False)
        self.vbox_address.set_sensitive(False)
    
    '''
    open_sweep_folder_chooser:
    Opens a Folder chooser. The user should then
    select a Folder (sweep) containing .xml scenarios'''    
    def open_sweep_folder_chooser(self, widget, data=None):
        if not self.sweep_folder_chooser_opened:
            self.sweep_folder_chooser_opened = True
            folder_chooser = gtk.FileChooserDialog('Choose sweep folder', self, gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER, ('ok',gtk.RESPONSE_OK)) 
            icon_path = os.path.join(os.getcwd(), 'application', 'common', 'om.ico')
            folder_chooser.set_icon_from_file(icon_path)
            folder_chooser.connect('response', self.select_sweep_folder)
            folder_chooser.connect('destroy', self.allow_open_sweep_folder_chooser)
            folder_chooser.show()
    
    '''
    show_seeds_entry:
    If toggle button is active, then the seeds nbr entry is shown'''        
    def show_seeds_entry(self, widget, data=None):
        self.vbox_seeds.set_sensitive(widget.get_active())
    
    '''
    show_db_entries:
    If toggle button is active, then the entries for db connection
    informations are shown'''    
    def show_db_entries(self, widget, data=None):
        self.vbox_login.set_sensitive(widget.get_active())
        self.vbox_passwd.set_sensitive(widget.get_active())
        self.vbox_address.set_sensitive(widget.get_active())
    
    '''
    allow_open_sweep_folder_chooser:
    Sets sweep_folder_chooser_opened to True. Then the user
    is able to reopen a sweep folder chooser dialog'''
    def allow_open_sweep_folder_chooser(self, widget, data=None):
        self.sweep_folder_chooser_opened = False
        
    '''
    select_sweep_folder:
    Selects a Sweep folder. Then a new tab is added in 
    the experiment creator containing an overview of all
    the scenarios contained in the folder'''
    def select_sweep_folder(self, widget, data):
        self.add_sweep_tab(widget.get_filename())
        widget.destroy()
    
    '''
    open_base_file_chooser:
    Opens a File chooser. The user should then 
    select a base scenario'''
    def open_base_file_chooser(self, widget, data=None):
        if not self.base_file_chooser_opened:
            self.base_file_chooser_opened = True
            base_file_chooser = gtk.FileChooserDialog('Choose base file', self, gtk.FILE_CHOOSER_ACTION_OPEN, ('ok', gtk.RESPONSE_OK))
            icon_path = os.path.join(os.getcwd(), 'application', 'common', 'om.ico')
            base_file_chooser.set_icon_from_file(icon_path)
            base_file_chooser.connect('response', self.select_base_file)
            base_file_chooser.connect('destroy', self.allow_open_base_file_chooser)
            base_file_chooser.show()
    
    '''
    allow_open_base_file_chooser:
    Sets base_file_chooser_opened to True. Then the user
    is able to reopen a new base file chooser dialog'''        
    def allow_open_base_file_chooser(self, widget, data=None):
        self.base_file_chooser_opened = False
    
    '''
    select_base_file:
    Selects the base scenario file. the filechooser
    widget is then destroyed'''    
    def select_base_file(self, widget, data):
        self.add_base_file(widget.get_filename())
        widget.destroy()
    
    '''
    add_base_file:
    Sets self.base_file_path to the given base file path.
    The base file path is then displayed on an entry.'''        
    def add_base_file(self, base_file_path):
        if(os.path.isfile(base_file_path)):
            path, name = os.path.split(base_file_path)
            name_split = str.split(name, '.')
            extension = name_split[len(name_split)-1]
            if extension == 'xml':
                self.base_file_path = base_file_path
                self.base_entry.set_text(base_file_path)
         
    '''
    add_sweep_tab:
    Adds a sweep tab (FileList object) if at least 1
    file with the extension xml is found in the sweep
    folder'''
    def add_sweep_tab(self, sweep_folder_path):
        fileList = None
        if(os.path.isdir(sweep_folder_path)):
            files = os.listdir(sweep_folder_path)
            for file in files:
                file_path = os.path.join(sweep_folder_path, file)
                if os.path.isfile(file_path):
                    name_split = str.split(file, '.')
                    extension = name_split[len(name_split)-1]
                    if extension == 'xml':
                        if fileList == None:
                            fileList = FileList(None, True)
                        fileList.add_file(file_path, file)
                        
        if not fileList == None:
            path, name = os.path.split(sweep_folder_path)
            label = self.create_tab_label(name, fileList, sweep_folder_path)
            self.sweeps_notebook.insert_page(fileList, label)
            self.sweeps_paths.append(sweep_folder_path)             
        
        
        
    '''
    create_tab_label:
    create a tab_label with an icon for closing the tab'''    
    def create_tab_label(self, title, fileList, sweep_folder_path):
        box = gtk.HBox(False, 0)
        label = gtk.Label(title)
        box.pack_start(label)
        
        close_image = gtk.image_new_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_MENU)
        image_w, image_h = gtk.icon_size_lookup(gtk.ICON_SIZE_MENU)

        close = gtk.Button()
        close.set_relief(gtk.RELIEF_NONE)
        close.set_focus_on_click(False)
        close.add(close_image)
        box.pack_start(close, False, False)
        
        style = gtk.RcStyle()
        style.xthickness = 0
        style.ythickness = 0
        close.modify_style(style)

        box.show_all()
        
        close.connect('clicked', self.removeSweep, fileList, sweep_folder_path)
        
        return box
    
    '''
    removeSweep:
    Removes a single sweep folder from the ExperimentCreatorDialog'''
    def removeSweep(self, sender, fileList, sweep_folder_path):
        page = self.sweeps_notebook.page_num(fileList)
        self.sweeps_notebook.remove_page(page)
        self.sweeps_paths.remove(sweep_folder_path)
        # Need to refresh the widget -- 
        # This forces the widget to redraw itself.
        self.sweeps_notebook.queue_draw_area(0,0,-1,-1)
        if(self.sweeps_notebook.get_n_pages()==0):
            self.hide()
    
    '''
    choose_action:
    This function is called when "response" callback is triggered.
    If the "response" is ok (-3) then start the creation, else (cancel)
    stop'''        
    def choose_action(self, widget, response_id):
        
        if response_id == -3:
            self.create_experiment_files()
        else:
            self.destroy()
    
    '''
    closed_creator:
    This function is called when "destroy" callback is triggered.
    This function sets NotebookFrame.creator_allready_open = False
    to allow the user to open a new experiment creator dialog'''        
    def closed_creator(self, widget, data=None):
        NotebookFrame.creator_allready_open = False
    
    '''
    create_experiment_files:
    Creates the input, output folders and the whole file structure for
    the experiment_creator.jar java application and then runs it'''    
    def create_experiment_files(self):
        
        base_folder = os.getcwd()
        not_actual_scenario = False
        
        self.status_label.set_text('The system is currently creating the File Structure for the experiment creator, please wait...')
        
        experiment_name = self.name_entry.get_text()
        experiment_name += '_'+ time.strftime("%d_%b_%Y_%H%M%S")
        
        experiment_folder = os.path.join(base_folder, 'run_scenarios', 'scenarios_to_run', experiment_name)
        os.mkdir(experiment_folder)
        
        input_folder = os.path.join(experiment_folder, 'input')
        output_folder = os.path.join(experiment_folder, 'output')
        os.mkdir(input_folder)
        os.mkdir(output_folder)
        
        if not self.is_using_right_schema_version(self.base_file_path):
            not_actual_scenario = True
        shutil.copy2(self.base_file_path, os.path.join(input_folder, 'base.xml'))
        testCommonDir = os.path.join(base_folder, 'application', 'common')
        shutil.copy2(os.path.join(testCommonDir ,'scenario_'+OpenMalariaRun.actual_scenario_version+'.xsd'), input_folder)
        
        i=0
        while i < self.sweeps_notebook.get_n_pages():
            fileList = self.sweeps_notebook.get_nth_page(i)
            sweep = fileList.return_sweep_list()
            
            first_sweep_path = sweep[0][0]
            sweep_path, tail = os.path.split(first_sweep_path)
            head, sweep_name = os.path.split(sweep_path)
            
            new_sweep_path = os.path.join(input_folder, sweep_name)
            os.mkdir(new_sweep_path)
            
            
            k = 0
            while k< len(sweep[0]):
                if os.path.isfile(sweep[0][k]):
                    if not self.is_using_right_schema_version(sweep[0][k]):
                        not_actual_scenario = True
                    shutil.copy2(sweep[0][k], new_sweep_path)
                
                if sweep[1][k]:
                    path, name = os.path.split(sweep[0][k])
                    os.rename(os.path.join(new_sweep_path, name), os.path.join(new_sweep_path, fileList.get_reference_type()+'.xml'))
                
                k+=1
            i+=1
                
        if not_actual_scenario:
            error = 'The scenario files are using another schema version than the supported one (schema vers.'+OpenMalariaRun.actual_scenario_version+').'
            error += '\nThe experiment creator will not be started.'
            error += '\nPlease change the schema version.'
            scenario_error_dialog = gtk.MessageDialog(self, gtk.DIALOG_MODAL,gtk.MESSAGE_ERROR,gtk.BUTTONS_NONE, error)
            scenario_error_dialog.add_button('Ok', gtk.RESPONSE_OK)
            scenario_error_dialog.run()
            scenario_error_dialog.destroy()
        else:
            self.status_label.set_text('The experiment creator is now started, please wait...')
            experimentCreator = ExperimentCreatorRun()
            experimentCreator.start_experimentCreator(input_folder, output_folder, self.mainFileList, self.get_seeds_nbr(), self.validate_checkbox.get_active())
        
        
        self.status_label.set_text('')    
        self.destroy()
                
    '''
    cancel_creation:
    If button cancel is clicked, then the experiment_creator dialog 
    is closed'''    
    def cancel_creation(self, widget, data=None):
        self.destroy()
        
    
    '''
    is_using_right_schema_version:
    Checks if the scenario is using the actual schema version'''
    def is_using_right_schema_version(self, file_path):
        if os.path.exists(file_path) and os.path.isfile(file_path):
            src=open(file_path)
            file_string=src.read()
            src.close()
        
            return re.search('xsi:noNamespaceSchemaLocation="scenario_'+OpenMalariaRun.actual_scenario_version +'.xsd"', file_string) != None
        else: 
            return False

    '''
    get_seeds_nbr(self):
    Returns the number of seeds set by the user. If an invalid 
    number is set, then the system will use 1'''
    def get_seeds_nbr(self):
        seeds_nbr = 0
        try:
            seeds_nbr = int(self.seeds_entry.get_text())
        except exceptions.ValueError:
            seeds_nbr = 1
        return seeds_nbr
      


'''
This class helps to build
for this application standardized frames (main window)
using three lines (top, middle, bottom).
top line: Load buttons, option buttons
middle line: Terminal
bottom line: Start/Stop buttons
'''
class NotebookFrame(gtk.Frame):
    
    def __init__(self, frame_name, parent, isWindows = False, isSimulatorFrame = True):
        gtk.Frame.__init__(self, frame_name)
        self.vertical_box = gtk.VBox(False, 10)
        self.vertical_box.show()
        self.lines_boxes = list()
        self.parent_window = parent
        self.fileList = FileList(self.parent_window)
        
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
        
        if(isSimulatorFrame):
            self.run_scenarios_base = os.path.join(base_folder, 'run_scenarios', 'scenarios_to_run')
            self.run_scenarios_outputs = os.path.join(base_folder, 'run_scenarios', 'outputs')
            self.liveGraphRun = LiveGraphRun()
            self.openMalariaRun = OpenMalariaRun()
            NotebookFrame.load_allready_open = False
            NotebookFrame.creator_allready_open = False
        else:
            self.run_scenarios_base = os.path.join(base_folder,'translate_scenarios', 'scenarios_to_translate')
            self.schemaTranslatorRun = SchemaTranslatorRun()
            
        self.isSimulatorFrame = isSimulatorFrame
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
        if not NotebookFrame.load_allready_open:
            self.scenarioChoice = ScenariosChoice(self.fileList, self.parent_window)
            NotebookFrame.load_allready_open = True
    
    '''
    add_object:
    Adds a widget in the window. The user just need to define 
    on which line/row (There are three lines/rows) he would like to
    put his new widget'''
    def add_object(self, line_number, window_object, at_start_h=True, resize=False):
            
        if(at_start_h):
            self.lines_boxes[line_number].pack_start(window_object, resize, resize)
        else:
            self.lines_boxes[line_number].pack_end(window_object, resize, resize)
        
        window_object.show()
    
    '''
    add_population_size_entry:
    Adds an entry and a checkbox widget to the tool.
    This entry is used for setting custom population's sizes'''
    def add_population_size_entry(self, line_number=0, at_start_h=True, resize=False):
        sim_population_size_vbox = gtk.VBox(False, 2)
        sim_population_size_label = gtk.Label('')
        
        sim_population_size_hbox = gtk.HBox(False, 2)
        self.sim_population_size_entry = gtk.Entry(25)
        self.sim_population_size_entry.set_text('100')
        self.sim_population_size_entry.set_sensitive(False)
        sim_population_size_checkbox = gtk.CheckButton('Custom population size ', False)
        sim_population_size_hbox.pack_start(sim_population_size_checkbox, False, False, 0)
        sim_population_size_hbox.pack_start(self.sim_population_size_entry, False, False, 0)
        
        sim_population_size_vbox.pack_start(sim_population_size_label)
        sim_population_size_vbox.pack_start(sim_population_size_hbox)
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
        output_folder_entry = gtk.Entry()
        output_folder_entry.set_text(self.run_scenarios_outputs)
        output_folder_entry.set_width_chars(113)
        output_folder_entry.set_sensitive(False)
        output_folder_button.connect('clicked', self.open_output_folder_chooser, output_folder_entry)
        output_folder_button_hbox.pack_start(output_folder_button, False, False, 0)
        output_folder_button_hbox.pack_start(output_folder_entry)
        
        output_folder_button_vbox.pack_start(output_folder_label, False, False, 2)
        output_folder_button_vbox.pack_start(output_folder_button_hbox, False, False, 2)
        output_folder_button_vbox.show_all()
        
        self.add_object(line_number, output_folder_button_vbox, at_start_h)
    
    '''
    open_output_folder_chooser:
    Opens a folder chooser dialog'''
    def open_output_folder_chooser(self, widget, entry):
        if not self.output_folder_chooser_opened:
            self.output_folder_chooser_opened = True
            folder_chooser = gtk.FileChooserDialog('Choose output folder', self.parent, gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER, ('ok',gtk.RESPONSE_OK)) 
            icon_path = os.path.join(os.getcwd(), 'application', 'common', 'om.ico')
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
        if not NotebookFrame.creator_allready_open:
            ExperimentCreatorDialog(self.fileList, self.parent_window)
            NotebookFrame.creator_allready_open = True
    
    '''
    reset_callback:
    Does a reset callback on the terminal object'''
    def reset_callback(self, widget, data=None):
        self.terminal.run_reset_callback()
        self.is_running = False

'''
class creating the openMalaria Tools UI'''
class OMFrontend:
    
    def delete_event(self, widget, event, data=None):
        return False
    
    '''
    destroy:
    Kills the actual window'''
    def destroy(self, widget, data=None):
        base_folder = os.getcwd()
        testSrcDir = os.path.join(base_folder, 'run_scenarios', 'scenarios_to_run')
        files = os.listdir(testSrcDir)
        for file in files:
            if os.path.isfile(os.path.join(testSrcDir, file)):
                os.remove(os.path.join(testSrcDir,file))
        gtk.main_quit()
        #sys.exit()
	os.kill(os.getpid(),signal.SIGTERM)
        
    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect("delete_event", self.delete_event)
        self.window.connect("destroy", self.destroy)
        self.window.set_border_width(10)
        self.window.set_title("openMalaria Tools")
        self.window.set_gravity(gtk.gdk.GRAVITY_NORTH_WEST)
        icon_path = os.path.join(os.getcwd(), 'application', 'common', 'om.ico')
    
        openmalaria = NotebookFrame('', self.window, True, True)
        
        openmalaria.add_import_button()
        openmalaria.add_experiment_creator_button()
        openmalaria.add_terminal()
        openmalaria.add_file_list()
        openmalaria.add_start_button()
        openmalaria.add_stop_button()
        openmalaria.add_outputs_frame()
        
        openmalaria.add_livegraph_option('Use Livegraph', '--liveGraph')
        openmalaria.add_option_button("Don't cleanup", '-c')
        openmalaria.add_option_button('Single output folder', 'only_one_folder')
        openmalaria.add_population_size_entry()
        openmalaria.add_output_folder_button()
        
        self.window.add(openmalaria)
        openmalaria.show()
        
        self.window.resize(gtk.gdk.screen_width(),gtk.gdk.screen_height())
        self.window.set_icon_from_file(icon_path)
        self.window.show()
        
    def main(self):
        gtk.main()
    
if __name__ == "__main__":
    omfrontend = OMFrontend()
    omfrontend.main()
        
