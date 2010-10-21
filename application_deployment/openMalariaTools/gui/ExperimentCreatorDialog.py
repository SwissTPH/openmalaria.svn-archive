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
        self.parent_window = parent
        
        
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
        
        label_experiment_vbox = gtk.VBox(False, 2)
        label_experiment_hbox = gtk.HBox(False, 2)
        experiment_folder_button = gtk.Button('Select output folder')
        self.experiment_folder_entry = gtk.Entry()
        self.experiment_folder_entry.set_width_chars(100)
        self.experiment_folder_entry.set_sensitive(False)
        self.experiment_folder_entry.set_text(os.path.join(os.getcwd(), 'run_scenarios', 'scenarios_to_run'))
        experiment_folder_button.connect('clicked', self.open_output_folder_chooser, self.experiment_folder_entry)
        label_experiment_hbox.pack_start(experiment_folder_button, False, False, 0)
        label_experiment_hbox.pack_start(self.experiment_folder_entry, True, True, 2)
        label_experiment_hbox.show_all()
        label_experiment_vbox.pack_start(label_experiment_hbox, False, False, 2)
        
        self.vbox.pack_start(label_experiment_vbox, False, False, 2)
        
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
        
        hbox_options.pack_start(vbox_1, False, False, 2)
        hbox_options.pack_start(vbox_2, False, False, 2)
        
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
        self.output_folder_chooser_opened=False
    
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
            folder_chooser.set_select_multiple(True)
            folder_chooser.connect('response', self.select_sweep_folder)
            folder_chooser.connect('destroy', self.allow_open_sweep_folder_chooser)
            folder_chooser.show()
    
    '''
    open_output_folder_chooser:
    Opens a Folder chooser. The user should then select
    a folder where the generated scenarios should be saved'''
    def open_output_folder_chooser(self, widget, entry):
        if not self.output_folder_chooser_opened:
            self.output_folder_chooser_opened = True
            folder_chooser = gtk.FileChooserDialog('Choose sweep folder', self, gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER, ('ok',gtk.RESPONSE_OK, 'cancel', gtk.RESPONSE_CANCEL)) 
            icon_path = os.path.join(os.getcwd(), 'application', 'common', 'om.ico')
            folder_chooser.set_icon_from_file(icon_path)
            folder_chooser.connect('response', self.add_output_folder, entry)
            folder_chooser.connect('destroy', self.allow_open_output_folder_chooser)
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
    allow_open_output_folder_chooser:
    Sets output_folder_chooser_opened to True. Then the user 
    is able to reopen an output folder chooser dialog'''
    def allow_open_output_folder_chooser(self, widget, data=None):
        self.output_folder_chooser_opened = False
        
    '''
    select_sweep_folder:
    Selects a Sweep folder. Then a new tab is added in 
    the experiment creator containing an overview of all
    the scenarios contained in the folder'''
    def select_sweep_folder(self, widget, response_id, data=None):
        if response_id == gtk.RESPONSE_OK:
            filenames = widget.get_filenames()
            for filename in filenames:
                self.add_sweep_tab(filename)
        widget.destroy()
    
    '''
    add_output_folder:
    Adds a user specific output folder'''    
    def add_output_folder(self, widget, response_id, entry):
        output_folder_path = widget.get_filename()
        if response_id == gtk.RESPONSE_OK:
            if(os.path.isdir(output_folder_path)):
                entry.set_text(output_folder_path)
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
            filter = gtk.FileFilter()
            filter.set_name("Xml files")
            filter.add_pattern("*.xml")
            base_file_chooser.add_filter(filter)
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
                translator = SchemaTranslatorRun()
                scenario_infos_list = list()
                input_path, input_file_name = os.path.split(base_file_path)
                short_name, extension = os.path.splitext(input_file_name)
                scenario_infos = list()
                scenario_infos.append(short_name)
                scenario_infos.append(base_file_path)
                scenario_infos_list.append(scenario_infos)
                
                scenario_infos_list = translator.check_and_return_runnable_scenarios(scenario_infos_list, self.parent_window)
                
                if len(scenario_infos_list)>0:    
                    self.base_file_path = scenario_infos_list[0][1]
                    self.base_entry.set_text(self.base_file_path)
         
    '''
    add_sweep_tab:
    Adds a sweep tab (FileList object) if at least 1
    file with the extension xml is found in the sweep
    folder'''
    def add_sweep_tab(self, sweep_folder_path):
        if(os.path.isdir(sweep_folder_path)):
            files = os.listdir(sweep_folder_path)
            valid_files = list()
            for file in files:
                file_path = os.path.join(sweep_folder_path, file)
                if os.path.isfile(file_path):
                    name_split = str.split(file, '.')
                    extension = name_split[len(name_split)-1]
                    if extension == 'xml':
                        valid_files.append(file_path)
        
        fileList = None
                        
        if len(valid_files) > 0:
            fileList = FileList(self.parent_window, True)
            fileList.addScenarios(valid_files,'sweep '+os.path.split(sweep_folder_path)[1] + ': ')
                        
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
        if response_id == gtk.RESPONSE_ACCEPT:
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
        
        if self.base_file_path == None:
            error = 'Base file undefined. Please choose a base file.'
            scenario_error_dialog = gtk.MessageDialog(self, gtk.DIALOG_MODAL,gtk.MESSAGE_ERROR,gtk.BUTTONS_NONE, error)
            scenario_error_dialog.add_button('Ok', gtk.RESPONSE_OK)
            scenario_error_dialog.run()
            scenario_error_dialog.destroy()
        
        else:
            not_actual_scenario = False
            
            self.status_label.set_text('The system is currently creating the File Structure for the experiment creator, please wait...')
            
            experiment_name = self.name_entry.get_text()
            experiment_name += '_'+ time.strftime("%d_%b_%Y_%H%M%S")
            
            experiment_folder = os.path.join(self.experiment_folder_entry.get_text(), experiment_name)
            if not os.path.exists(experiment_folder):
                os.mkdir(experiment_folder)
            
            input_folder = os.path.join(experiment_folder, 'input')
            output_folder = os.path.join(experiment_folder, 'output')
            os.mkdir(input_folder)
            os.mkdir(output_folder)
            
            if not self.is_using_right_schema_version(self.base_file_path):
                not_actual_scenario = True
            shutil.copy2(self.base_file_path, os.path.join(input_folder, 'base.xml'))
            base_folder = os.getcwd()
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
                
                if os.path.exists(new_sweep_path):
                    filenames = list()
                    for filename in os.listdir(input_folder):
                        filenames.append(filename)
                    test_sweep_name = sweep_name
                    i = 1
                    
                    while(filenames.count(test_sweep_name)>0):
                        test_sweep_name = sweep_name + '_'+str(i)
                        i = i + 1 
                         
                    new_sweep_path = os.path.join(input_folder, test_sweep_name)
                     
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
                self.status_label.set_text("The experiment's files are now generated... Please wait...")
                time.sleep(.2)
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