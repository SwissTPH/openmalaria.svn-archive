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
import signal

from openMalariaTools.gui.NotebookFrame import NotebookFrame
from openMalariaTools.utils.PathsAndSchema import PathsAndSchema

'''
class creating the openMalaria Tools UI'''
class OMFrontend:
    
    def delete_event(self, widget, event, data=None):
        return False
    
    '''
    destroy:
    Kills the actual window'''
    def destroy(self, widget, data=None):
        #gtk.main_quit()
        #sys.exit()
	    os.kill(os.getpid(),signal.SIGTERM)
        
    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect("delete_event", self.delete_event)
        self.window.connect("destroy", self.destroy)
        self.window.set_border_width(10)
        self.window.set_title("openMalaria Tools")
        self.window.set_gravity(gtk.gdk.GRAVITY_NORTH_WEST)
        icon_path = PathsAndSchema.get_icon_path()
    
        openmalaria = NotebookFrame('', self.window, True)
        
        openmalaria.add_import_button()
        openmalaria.add_experiment_creator_button()
        openmalaria.add_terminal()
        openmalaria.add_file_list()
        openmalaria.add_start_button()
        openmalaria.add_stop_button()
        openmalaria.add_outputs_frame()
        
        openmalaria.add_livegraph_option('Use Livegraph', '--liveGraph')
        openmalaria.add_option_button('Single output folder', 'only_one_folder')
        openmalaria.add_population_size_entry()
        openmalaria.add_output_folder_button()
        
        self.window.add(openmalaria)
        openmalaria.show()
        
        self.window.maximize()
        self.window.set_icon_from_file(icon_path)
        self.window.show()
        
    def main(self):
        gtk.main()
    
if __name__ == "__main__":
    omfrontend = OMFrontend()
    omfrontend.main()
        
