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
import pygtk
if not sys.platform == 'win32':
    pygtk.require('2.0')
import gtk

from ..utils.PathsAndSchema import PathsAndSchema

'''
CustomMessageDialog:
Instead of replicating gtk.MessageDialog invocation in the code,
this helper class allows us to create custom message dialogs.'''
class CustomMessageDialogs():
    
    NONE_TYPE = -1
    SCHEMA_TRANSLATOR_TYPE = 0
    
    '''
    show_message_dialog:
    Creates a message dialog and shows it'''
    @staticmethod
    def show_message_dialog(parent_window, message_type, message_text, parent_type=-1, parent_class=None, args=None):
        custom_message_dialog = gtk.MessageDialog(parent_window, gtk.DIALOG_MODAL, message_type, gtk.BUTTONS_NONE, message_text)
        
        icon_path = PathsAndSchema.get_icon_path()
        custom_message_dialog.set_icon_from_file(icon_path)
        
        if(message_type == gtk.MESSAGE_ERROR):
            custom_message_dialog.add_button('Ok', gtk.RESPONSE_OK)
        
        if(message_type == gtk.MESSAGE_WARNING):
            if(parent_type == CustomMessageDialogs.SCHEMA_TRANSLATOR_TYPE):
                custom_message_dialog.add_button('Yes', gtk.RESPONSE_YES)
                custom_message_dialog.add_button('No', gtk.RESPONSE_NO)
                custom_message_dialog.add_button('Cancel', gtk.RESPONSE_CANCEL)
                custom_message_dialog.connect('response', parent_class.init_translation, parent_window, args[0])
                
                
        custom_message_dialog.run()
        custom_message_dialog.destroy()
        
        