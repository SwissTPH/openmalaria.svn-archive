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

from xml.dom.minidom import parse
from xml.dom.minidom import Node

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