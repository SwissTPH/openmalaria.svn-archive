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
import xml.dom
from xml.dom.minidom import parse
from xml.dom.minidom import Node

from VirtualTerminal import VirtualTerminal
from OpenMalariaRun import OpenMalariaRun
from JavaAppsRun import SchemaTranslatorRun
from JavaAppsRun import LiveGraphRun

'''
FileViewersContainers(gtk.Window):
Window containing all the loaded scenarios.
Every scenario will be added in a notebook.
'''
class FileViewersContainer(gtk.Window):
    
    
    def __init__(self):
        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
        self.set_border_width(10)
        self.set_title("Scenarios")
        self.notebook = gtk.Notebook()
        self.notebook.set_tab_pos(gtk.POS_TOP)
        self.connect('delete-event', self.nothing)
        self.add(self.notebook)
        self.show_all()
        self.filenames = list()
        self.names = list()
    
    '''
    Add new scenarios in the container and set the filenames
    '''    
    def addScenarios(self, filenames):
        only_files = list()
        only_files_names = list()
        for i in range(len(filenames)):
            actual_filename = filenames[i]
            if not(os.path.isdir(actual_filename)):
                only_files.append(actual_filename)
                split_filename = string.split(actual_filename, '/')
                actual_name = split_filename[len(split_filename)-1]
                only_files_names.append(string.split(actual_name, '.')[0])
                actual_fileViewer = FileViewer('')
                actual_fileViewer.parseFile(actual_filename, '')
                self.notebook.append_page(actual_fileViewer, gtk.Label(actual_name))
        self.filenames = only_files
        self.names = only_files_names
    
    '''
    Before a new load, the actual "fileviewers" are removed from the notebook
    '''    
    def removeScenarios(self):
        for i in range(self.notebook.get_n_pages()):
            self.notebook.remove_page(0)
            
    def nothing(self, widget, data=None):
        return True
    
    def getActualFilenames(self):
        return self.filenames
    
    def getActualNames(self):
        return self.names
        
'''
The FileViewer allows the user to see the scenarios
as a tree representation.
'''
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
    The scenario file is parsed to create the tree representation.
    ParseFile is the initialization function. This function is followed
    by parseFileRec which does a depth-first recursion on every nodes
    '''    
    def parseFile(self, file_path, scenario_name):
        self.actual_path = file_path
        self.tcolumn.set_title(scenario_name)
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
                    attr_node = self.treestore.append(root_tree)
                    self.treestore.set(attr_node, 
                     self.COL_NODE_NAME, attributes.item(i).nodeName, 
                     self.COL_NODE_VALUE, attributes.item(i).nodeValue,
                     self.COL_NODE_TYPE, self.ATTRIBUTE_NODE,
                     self.COL_NODE_OBJECT, attributes.item(i))
                ending_node = self.treestore.append(root_tree)
                self.treestore.set(ending_node,
                                   self.COL_NODE_NAME, '>',
                                   self.COL_NODE_VALUE, None,
                                   self.COL_NODE_TYPE, self.ELEMENT_NODE,
                                   self.COL_NODE_OBJECT, None)
        
        children = root.childNodes
        self.parseFileRec(children, root_tree)
        
        element_ending = self.treestore.append(root_tree)
        self.treestore.set(element_ending,
                           self.COL_NODE_NAME, '</ '+root.nodeName+' >',
                           self.COL_NODE_VALUE, None,
                           self.COL_NODE_TYPE, self.ELEMENT_NODE,
                           self.COL_NODE_OBJECT, None)
                
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
    def __init__(self, fileviewersContainer):
        gtk.FileChooserDialog.__init__(self, 'Scenarios to run...', None, gtk.FILE_CHOOSER_ACTION_OPEN, ('load',gtk.RESPONSE_OK))
        
        self.set_border_width(10)
        self.set_select_multiple(True)
        
        base_folder = os.getcwd()
        self.run_scenarios_base = base_folder + "/run_scenarios/scenarios_to_run"
        self.set_current_folder(self.run_scenarios_base)
        
        self.fileviewersContainer = fileviewersContainer
        self.connect('response', self.updateFileViewerContainer)
        
        filter = gtk.FileFilter()
        filter.set_name("Xml files")
        filter.add_pattern("*.xml")
        self.add_filter(filter)
        
        self.show()
    '''
    updateFileViewerContainer:
    update the FileViewerContainer when new scenarios are selected
    and the load button has been clicked.
    '''
    def updateFileViewerContainer(self, widget, data=None):
        self.fileviewersContainer.removeScenarios()
        scenarios = self.importScenarios()
        self.fileviewersContainer.addScenarios(scenarios)
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
        
        return self.run_scenarios_base + '/' + imported_name

'''
This class helps to build
for this application standardized frames (main window)
using three lines (top, middle, bottom).
top line: Load buttons, option buttons
middle line: Terminal
bottom line: Start/Stop buttons
'''
class NotebookFrame(gtk.Frame):
    def __init__(self, frame_name, isSimulatorFrame = True, fileViewerContainer = None):
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
        
        self.fileviewerContainer = fileViewerContainer
        
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
        
        filenames = self.fileviewerContainer.getActualFilenames()
        names = self.fileviewerContainer.getActualNames()
        
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
            
        
        for i in range(len(filenames)):
            self.openMalariaRun.runScenario(self.terminal, self.liveGraphRun, filenames[i], names[i], checkpointing, nocleanup, use_livegraph)  
    
    def schemaTranslatorCommand(self, widget, data=None):
        command = self.schemaTranslatorRun.get_schemaTranslator_command()
        
        for i in range(len(self.options)):
            option = self.options[i]
            if(option[0].get_active()):
                command = command +' '+option[1]
                  
        self.terminal.run_command(command)
    
    def openNewDialog(self, widget, data=None):
        self.scenarioChoice = ScenariosChoice(self.fileviewerContainer)
    
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
    
    def add_start_button(self, at_start_h=True, cbox_line_number=0, button_line_number=2, title="Start", simulator=True):
        if(self.first_start_button):
            if(simulator):
                start_button = gtk.Button(title)
                #self.start_cbox = self.add_scenario_cbox(at_start_h, cbox_line_number)
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

'''
class creating the openMalaria Tools UI
'''
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
        
        self.fileviewersContainer = FileViewersContainer()
        openmalaria = NotebookFrame('', True, self.fileviewersContainer)
        schemaTranslator = NotebookFrame('', False)
        notebook.append_page(openmalaria, gtk.Label('openMalaria'))
        notebook.append_page(schemaTranslator, gtk.Label('schemaTranslator'))
        
        openmalaria.add_import_button()
        openmalaria.add_terminal()
        openmalaria.add_start_button()
        openmalaria.add_stop_button()
        
        openmalaria.add_option_button('Use Livegraph', '--liveGraph')
        openmalaria.add_option_button('Checkpointing', '-- --checkpoint')
        openmalaria.add_option_button("Don't cleanup", '-c')
        
        '''
            second part: schemaTranslator
        '''
        
        schemaTranslator.add_import_button()
        schemaTranslator.add_terminal()
        schemaTranslator.add_start_button(True,0,2,"Start translation", False)
        
        self.window.add(notebook)
        
        openmalaria.show()
        schemaTranslator.show()
        notebook.show()
        self.window.move(0,0)
        self.fileviewersContainer.resize(self.window.get_size()[0]/2, self.window.get_size()[1])
        self.fileviewersContainer.move(self.window.get_size()[0]+5, self.window.get_position()[1])
        self.fileviewersContainer.show()
        self.window.show()
        
    def main(self):
        gtk.main()
    
if __name__ == "__main__":
    omfrontend = OMFrontend()
    omfrontend.main()
        
