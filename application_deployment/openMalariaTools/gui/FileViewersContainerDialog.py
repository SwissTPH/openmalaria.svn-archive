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

from FileViewerFrame import FileViewer
from ..utils.PathsAndSchema import PathsAndSchema

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
        
        icon_path = PathsAndSchema.get_icon_path()
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