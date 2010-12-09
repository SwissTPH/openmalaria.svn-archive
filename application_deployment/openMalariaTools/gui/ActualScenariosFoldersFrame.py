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

from ..utils.PositionContainer import PositionContainer

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
        self.tcolumn2.set_clickable(True)
        self.tcolumn2.connect('clicked', self.arrange_filenames)
        
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
        
        hbox = gtk.HBox(False, 2)
        
        self.scrolledWindow = gtk.ScrolledWindow()
        self.scrolledWindow.add_with_viewport(self.treeview)
        self.scrolledWindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        
        '''hbox.pack_start(self.scrolledWindow, True, True, 2)
        
        vbox_button = gtk.VBox(False, 2)
        
        clear_button = gtk.Button("Clear")
        #clear_button.connect('clicked', self.openNewDialog)
        vbox_button.pack_end(clear_button, False, False, 2)
        hbox.pack_start(vbox_button, False, False, 2)'''
        
        self.First = True
        self.reverse_order = False

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
    arrange_filenames:
    Arranges all the filenames in the liststore
    '''
    def arrange_filenames(self, widget):
        self.reverse_order = not self.reverse_order
            
        positionContainer = PositionContainer(self.reverse_order)
        actual_position = 0
        
        iterator = self.liststore.get_iter_first()
        
        while iterator:
            name = self.liststore.get_value(iterator, 2)
            
            positionContainer.add(name, actual_position)
            
            actual_position += 1
            iterator = self.liststore.iter_next(iterator)
        
        self.liststore.reorder(positionContainer.get_positions_numbers())   
