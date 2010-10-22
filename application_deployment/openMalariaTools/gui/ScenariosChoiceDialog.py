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
import string

from ..utils.PathsAndSchema import PathsAndSchema


'''
A specific FileChooserDialog:
One or more scenario files are selected, then those are loaded in the fileviewer container as trees
The FileChooserDialog is then closed.
'''
class ScenariosChoice(gtk.FileChooserDialog):
    def __init__(self, fileList, parent,notebookFrame = None):
        gtk.FileChooserDialog.__init__(self, 'Scenarios to run...', parent, gtk.FILE_CHOOSER_ACTION_OPEN, ('load',gtk.RESPONSE_OK, 'cancel', gtk.RESPONSE_CANCEL))
        icon_path = PathsAndSchema.get_icon_path()
        self.set_icon_from_file(icon_path)
        
        self.set_border_width(10)
        self.set_select_multiple(True)
        
        self.notebookFrame = notebookFrame
        
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
        self.notebookFrame.load_allready_open = False
    
    '''
    updateFileViewerContainer:
    update the FileViewerContainer when new scenarios are selected
    and the load button has been clicked.
    '''
    def updateFileList(self, widget, response_id, data=None):
        if response_id == gtk.RESPONSE_OK:
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
        '''selectedFolder = self.get_current_folder()
        if not (selectedFolder == self.run_scenarios_base):
            for i in range(len(selectedFiles)):
                selectedFiles[i] = self.importScenario(selectedFiles[i])'''
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