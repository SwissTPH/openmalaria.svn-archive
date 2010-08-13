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

# Imports

import os
import threading
import locale
import gobject
import gtk
import time
import subprocess

class VirtualTerminal_win(gtk.ScrolledWindow):
    
    def __init__(self):
        gtk.ScrolledWindow.__init__(self)
        self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        gobject.threads_init()
        #gtk.gdk.threads_init()
        encoding = locale.getpreferredencoding()
        self.utf8conv = lambda x : unicode(x, encoding).encode('utf8')
        self.textView = gtk.TextView()
        self.add(self.textView)
        self.textView.show()
        self.thr = None

    def start_thread(self, argv, directory):
        self.thr = threading.Thread(target= self.read_output, args=(argv, directory))
        self.thr.start()
    
    def read_output(self, argv, directory):
        stdin, stdouterr = subprocess.Popen(argv, bufsize=0, executable=argv[0], stdin=None, stdout=None, stderr=None, preexec_fn=None, close_fds=False, shell=False, cwd=directory, env=None, universal_newlines=False, startupinfo=None, creationflags=0)
        buffer = self.textView.get_buffer()
        while 1:
            line = stdouterr.readline()
            if not line:
                break
            gtk.gdk.threads_enter()
            iter = buffer.get_end_iter()
            buffer.place_cursor(iter)
            buffer.insert(iter, self.utf8conv(line))
            self.textView.scroll_to_mark(buffer.get_insert(), 0.1)
            gtk.gdk.threads_leave()
            
    def is_thread_running(self):
        return self.thr != None and self.thr.isAlive()
    
    def stop_thread(self):
        if self.is_thread_running():
            self.thr.__stop()
            
    def stop_thread_and_output(self):
        if self.is_thread_running():
            self.thr.__stop()
            buffer = self.textView.get_buffer()
            iter = buffer.get_end_iter()
            buffer.place_cursor(iter)
            buffer.insert(iter, self.utf8conv('The simulation has been stopped...'))
    
    def feed_command(self, line):
        buffer = self.textView.get_buffer()
        iter = buffer.get_end_iter()
        buffer.place_cursor(iter)
        buffer.insert(iter, self.utf8conv(line))
        iter = buffer.get_end_iter()
        buffer.place_cursor(iter)
        buffer.insert(iter, '\n')     
    
    def run_openmalaria_command(self, command_string, simDir, livegraph, ctsoutFile, runLiveGraph=False):
        
        self.stop_thread()
        
        command = command_string.split(' ')
        self.start_thread(command, simDir)

        while self.is_thread_running():
            if runLiveGraph:
                    if(os.path.isfile(ctsoutFile)): 
                        livegraph.start_liveGraph(simDir, ctsoutFile)
                        runLiveGraph = False
            time.sleep(.01)
            #time.sleep(.01)
            #gtk.main_iteration()
