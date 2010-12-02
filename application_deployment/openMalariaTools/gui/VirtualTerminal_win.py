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
import sys
import pygtk
if not sys.platform == 'win32':
    pygtk.require('2.0')
import gtk

import os
import threading
import locale
import time
import subprocess
import re
import ctypes
import signal

from ..tools_management.JavaAppsRun import LiveGraphRun

'''StreamHelper:
Class (Thread) for handling the stdout, stderr streams and check the application status''' 
class StreamHelper():   
    def __init__(self, file_stream):
        self.file_stream = file_stream
        self.is_ready = False
        self.line_output = ''
        self.isRunning = True
        self.openMalariaFinished = False
        self.is_percentage = False
        self.alive = True
        self.sim_end = False
        self.thread = threading.Thread(None, self.start)
        self.thread.start()
        
        self.tics = 0;
        
    '''start:
    Starts the streamhelper's Thread. While the thread is alive, it updates and monitors
    the streams status.'''
    def start(self):
        while(self.alive):
            total_string = ''
            while not self.is_ready:
                char = self.file_stream.read(1)
                if(char == ' ' or char == '') and self.openMalariaFinished:
                    time.sleep(.2)
                    if self.tics == 2:
                        self.is_ready = True
                        self.alive = False
                    self.tics += 1
                else:
                    self.tics = 0
                    
                if(char == '\r' or char == '\n' or char == '\r\n'):
                    if(total_string == 'sim end'):
                        self.sim_end = True
                    self.line_output = total_string
                    percent = re.search('[\d%]', total_string)
                    if(percent != None):
                        self.is_percentage = True
                    else:
                        self.is_percentage = False
                        
                    self.is_ready = True
                else:
                    total_string += char
        self.file_stream.close()
    
    '''
    setOpenMalariaFinished:
    Sets that the openmalaria simulation is finished'''                
    def setOpenMalariaFinished(self):
        self.openMalariaFinished = True
    
    '''
    isPercentage:
    Every lines red from stderr and stdout are checked, and
    if a string containing the template [\d%] is found, then
    is_percentage is set to True. This function is useful for
    the progressbar used in the object VirtualTerminal_win'''     
    def isPercentage(self):
        return self.is_percentage
    
    '''
    isAlive:
    Returns the thread current status'''
    def isAlive(self):
        return self.alive
    
    '''
    isReady:
    If the thread has content to returns to the terminal, then
    it is set to is_ready.'''
    def isReady(self):
        return self.is_ready
    
    '''
    isSimEnd:
    Returns True if the stdout has returned the sim end string'''
    def isSimEnd(self):
        return self.sim_end
    
    '''
    setNotReady:
    Sets is_ready to false. This happens when the terminal has red
    the actual content and allows the thread to seek for new content'''
    def setNotReady(self):
        self.is_ready = False
    
    '''
    getOutput:
    Returns the stderr or stdout actual content'''
    def getOutput(self):
        return self.line_output
    
    '''
    reset_callback:
    kills the thread'''
    def reset_callback(self):
        self.alive = False

''' Since there is no vte.Terminal implementation on windows, 
we have created a specific Virtual Terminal for openmalaria on windows'''
class VirtualTerminal_win(gtk.ScrolledWindow):
    
    RED = 0
    GREEN = 1
    GOLD = 2
    WHITE = 3
    
    def __init__(self):
        gtk.ScrolledWindow.__init__(self)
        self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        encoding = locale.getpreferredencoding()
        self.utf8conv = lambda x : unicode(x, encoding).encode('utf8')
        self.textView = gtk.TextView()
        self.textView.modify_base(0, gtk.gdk.Color(red=0, green=0, blue=0))
        self.textView.set_wrap_mode(gtk.WRAP_WORD_CHAR)
        self.textView.set_left_margin(4)
        self.add(self.textView)
        self.textView.show()
        self.userStop = False
        self.isRunning = False
        self.livegraph = None  
 
    ''' read_output:
	Creates the subprocess openmalaria, the two threads waiting output from stdout and stderr
    and manages the outputs incoming from openmalaria'''
    def read_output(self, argv, directory, ctsoutFile, runLiveGraph):
        self.isRunning = True
        
        advance = 0.0
        sub = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=directory)
        
        buf = self.textView.get_buffer()
        self.livegraph = LiveGraphRun()
        
        streams = list()
        stdout_helper = StreamHelper(sub.stdout)
        stderr_helper = StreamHelper(sub.stderr)
        First = True
        end_iter = None
        mark = None
        progressbar = None
        i = 0;
                 
        while stdout_helper.isAlive() or stderr_helper.isAlive():
            
            if runLiveGraph:
                if(os.path.isfile(ctsoutFile)):
                    print ctsoutFile 
                    self.livegraph.start_liveGraph(directory, ctsoutFile)
                    runLiveGraph = False
            
            if(self.userStop):
                stderr_helper.reset_callback()
                stdout_helper.reset_callback()
                #self.kill_win(sub.pid)
                if sub.poll()==None:
                    sub.terminate()
                        
            
            if(sub.poll()!=None):
                stderr_helper.setOpenMalariaFinished()
                stdout_helper.setOpenMalariaFinished()
            
            if stdout_helper.isReady():
                    
                if stdout_helper.isPercentage():
                    if progressbar == None:
                        progressbar = gtk.ProgressBar(adjustment=None)
                        mark = buf.create_mark('mark', buf.get_end_iter(), left_gravity=True)
                        anchor = buf.create_child_anchor(buf.get_iter_at_mark(mark))
                        self.textView.add_child_at_anchor(progressbar, anchor)
                        progressbar.show()
                    if(stderr_helper.isSimEnd()):
                        progressbar.set_fraction(1)
                        advance = 1.0
                        stdout_helper.reset_callback()
                    else:
                        if(advance < 1):
                            advance = progressbar.get_fraction()+0.01
                        else:
                            advance = 1
                        
                        progressbar.set_fraction(advance)
                    
                else:
                    iter = buf.get_end_iter()
                    buf.insert_with_tags_by_name(iter, self.utf8conv(stdout_helper.getOutput()+'\n'), 'gold-tag')
                       
                stdout_helper.setNotReady() 
                
            if stderr_helper.isReady():
                iter = buf.get_end_iter()
                buf.insert_with_tags_by_name(buf.get_end_iter(), self.utf8conv('\n'+stderr_helper.getOutput()), 'red-tag')
                stderr_helper.setNotReady()
                
            while(gtk.events_pending()):
                gtk.main_iteration()
         
        self.isRunning = False
        
        return advance >= 1.0
    
    '''kill_win:
    Windows specific process killing'''
    def kill_win(self,pid):
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.OpenProcess(1, 0, pid)
        return (0 != kernel32.TerminateProcess(handle, 0)) 
    
	'''run_reset_callback(self):
 	This function stops the read_output function, and so stops the openmalaria simulation'''
    def run_reset_callback(self):
        self.userStop = True
        buffer = self.textView.get_buffer()
        iter = buffer.get_end_iter()
        buffer.place_cursor(iter)
        if(self.livegraph != None):
            self.livegraph.quit_livegraph()
            self.livegraph = None
        buffer.insert_with_tags_by_name(iter, self.utf8conv('\nThe simulation has been stopped... \n'), 'red-tag')
    
	'''feed_command(self, line, colorCode):
	This function is used to output text in the gtk.TextView object used to mimic a terminal'''	
    def feed_command(self, line, colorCode = None):
        buffer = self.textView.get_buffer()
        iter = buffer.get_end_iter()
        if colorCode == None:
            buffer.insert_with_tags_by_name(iter, self.utf8conv(line), 'white-tag')
        elif colorCode == VirtualTerminal_win.GREEN :
            buffer.insert_with_tags_by_name(iter, self.utf8conv(line), 'green-tag')
        elif colorCode == VirtualTerminal_win.GOLD:
            buffer.insert_with_tags_by_name(iter, self.utf8conv(line), 'gold-tag')
        elif colorCode == VirtualTerminal_win.RED:
            buffer.insert_with_tags_by_name(iter, self.utf8conv(line), 'red-tag')
        buffer.insert(iter, '\n')         
    
	'''run_openmalaria_command(self, command_string, simDir, livegraph, ctsoutFile, runLiveGraph):
	start the openmalaria simulation by invoking the read_output function'''
    def run_openmalaria_command(self, command_list, simDir, livegraph, ctsoutFile, runLiveGraph=False):
        self.userStop = False
        return self.read_output(command_list, simDir, ctsoutFile, runLiveGraph)
    
    def init_new_buffer(self):
        self.textView.set_buffer(gtk.TextBuffer())
        
        buffer = self.textView.get_buffer()
        
        green_color = gtk.gdk.Color(red=26985, green=35723, blue=26985)
        gold_color = gtk.gdk.Color(red=65535, green=65535, blue=0)
        red_color = gtk.gdk.Color(red=65535, green=0, blue=0)
        white_color = gtk.gdk.Color(red=65535, green=65535, blue=65535)
        
        self.red_tag = buffer.create_tag('red-tag')
        self.red_tag.set_property("foreground-gdk", red_color)
        self.gold_tag = buffer.create_tag('gold-tag')
        self.gold_tag.set_property("foreground-gdk", gold_color)
        self.green_tag = buffer.create_tag('green-tag')
        self.green_tag.set_property("foreground-gdk", green_color)
        self.white_tag = buffer.create_tag('white-tag')
        self.white_tag.set_property("foreground-gdk", white_color) 
        
