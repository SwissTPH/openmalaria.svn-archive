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
import tempfile
import glob
import time
import subprocess
import shutil
import gzip
import re

from ..utils.PathsAndSchema import PathsAndSchema
from ..gui.VirtualTerminal_win import VirtualTerminal_win
from JavaAppsRun import LiveGraphRun
from datetime import date

'''
OpenMalariaRun:
This object provides all the arguments, inputs and outputs
for the openmalaria executable'''
class OpenMalariaRun():
    
    #base_folder = os.getcwd()
    #sys.path[0] = os.path.join(base_folder, 'application', 'common')
    #import compareOutput
    #import compareCtsout
    
    
    def findFile (self, execName):
        
        execs=set()
        for name in [execName]:
            path=os.path.join(PathsAndSchema.get_application_folder(),name)
            if os.path.isfile (path):
                execs.add (path)
        
        if not execs:
            print "Unable to find: openMalaria[.exe]; please compile it."
            sys.exit(-1)
        
        newest=None
        for path in execs:
            if newest is None or os.path.getmtime(path) > os.path.getmtime(newest):
                newest=path
                return newest
            
    
    def linkOrCopy (self, src, dest):
        if hasattr(os, 'symlink'):
            os.symlink(os.path.abspath(src), dest)
        else:
            shutil.copy2(src, dest)
    
    '''
    runScenario:
    runs a Scenario using the openmalaria executable.
    '''
    def runScenario(self, terminal, livegraph, path, name, simDir, only_one_folder, custom_pop_size=0, use_custom_pop_size=False, checkpointing=False, nocleanup=False, runLiveGraph=False, newBuffer=False):
        
        if newBuffer:
            terminal.init_new_buffer()
        
        scenarioSrc = path
        
        if sys.platform in ['win32','cygwin']:
            openMalariaExec=os.path.abspath(self.findFile ("openMalaria.exe"))
        else:
            openMalariaExec=os.path.abspath(self.findFile ("openMalaria"))
        success = False
        
        arglist = list()
        arglist.append(openMalariaExec)
        arglist.append('--resource-path')
        arglist.append(simDir)
        arglist.append('--scenario')
        
        shutil.copy2(scenarioSrc, simDir)
        head, tail = os.path.split(scenarioSrc)
        scenarioDest = os.path.join(simDir, tail)
        
        if(use_custom_pop_size):
            if custom_pop_size > 0:
                src=open(scenarioDest)
                scen_string=src.read()
                src.close()
                
                scen_string = re.sub('popSize="\d*"', 'popSize="'+str(custom_pop_size)+'"', scen_string)
                
                dest= open(scenarioDest, 'w')
                dest.write(scen_string)
                dest.close()
            else:
                terminal.feed_command('WARNING: Invalid custom population size, the simulation will be run without any population size changes', terminal.RED)
        
        arglist.append(scenarioDest)
        
        cmd_string = openMalariaExec+" --resource-path "+simDir+" --scenario "+scenarioDest
        
        '''if(checkpointing):
            cmd = cmd+ --checkpoint'''
        
        outputFile=os.path.join(simDir,"output.txt")
        outputGzFile=os.path.join(simDir,"output.txt.gz")
        ctsoutFile=os.path.join(simDir,"ctsout.txt")
        ctsoutGzFile=os.path.join(simDir,"ctsout.txt.gz")
        checkFile=os.path.join(simDir,"checkpoint")
            
        
        # Link or copy required files.
        # The schema file only needs to be copied in BOINC mode, since otherwise the
        # scenario is opened with a path and the schema can be found in the same
        # directory. We copy it anyway.
        scenario_xsd=os.path.join(simDir,'scenario_'+PathsAndSchema.get_actual_schema()+'.xsd')
        densities_csv=os.path.join(simDir, 'densities.csv')
        if not os.path.exists(scenario_xsd):
            shutil.copy2(os.path.join(PathsAndSchema.get_common_folder() ,'scenario_'+PathsAndSchema.get_actual_schema()+'.xsd'), scenario_xsd)
        if not os.path.exists(densities_csv):
            shutil.copy2(os.path.join(PathsAndSchema.get_common_folder(), 'densities.csv'), densities_csv)
        
        terminal.feed_command(time.strftime("%a, %d %b %Y %H:%M:%S")+"   %s.xml" % name, terminal.GOLD)
            
        startTime=lastTime=time.time()
    
        while (not os.path.isfile(outputFile)):
            #terminal.feed_command("\033[0;32m  "+cmd+"\033[0;00m")
            terminal.feed_command(cmd_string)
            success = terminal.run_openmalaria_command(arglist, simDir, livegraph, ctsoutFile, runLiveGraph)
            
            if (os.path.isfile(outputGzFile)) and (not os.path.isfile(outputFile)):
                f_in = gzip.open(outputGzFile, 'rb')
                f_out = open(outputFile, 'wb')
                f_out.writelines(f_in)
                f_out.close()
                f_in.close()
                os.remove(outputGzFile)
            
            # check for ctsout.txt.gz in place of ctsout.txt and uncompress:
            if (os.path.isfile(ctsoutGzFile)) and (not os.path.isfile(ctsoutFile)):
                f_in = gzip.open(ctsoutGzFile, 'rb')
                f_out = open(ctsoutFile, 'wb')
                f_out.writelines(f_in)
                f_out.close()
                f_in.close()
                os.remove(ctsoutGzFile)
            
            # if the checkpoint file hasn't been updated, stop
            if not os.path.isfile(checkFile):
                break
            checkTime=os.path.getmtime(checkFile)
            if not checkTime > lastTime:
                break
            lastTime=checkTime	
            
        terminal.feed_command("Done in " + str(time.time()-startTime) + " seconds", terminal.GOLD)
        
        if not nocleanup:
            for f in (glob.glob(os.path.join(simDir,"checkpoint*")) + glob.glob(os.path.join(simDir,"seed?")) + [os.path.join(simDir,"init_data.xml"),os.path.join(simDir,"boinc_finish_called"),os.path.join(simDir,"scenario.sum")]):
                if os.path.isfile(f):
                    os.remove(f)
        
        if only_one_folder:
            if os.path.exists(outputFile):
                os.rename(outputFile, os.path.join(simDir, name + '.txt'))
            if os.path.exists(ctsoutFile) and not runLiveGraph:
                os.rename(ctsoutFile, os.path.join(simDir, 'ct_'+name+'.txt'))
        
        # Compare outputs:
        #if ret == 0:
            # ctsout.txt (this output is optional):
            '''if os.path.isfile(ctsoutFile):
                origCtsout = os.path.join(simDir,"expected/ctsout%s.txt"%name)
                newCtsout = os.path.join(simDir,"ctsout%s.txt"%name)
                if os.path.isfile(origCtsout):
                    ctsret,ctsident = compareCtsout.main (origCtsout, ctsoutFile)
                else:
                    ctsret,ctsident = 3,False
                    terminal.feed_command("\033[1;31mNo original ctsout.txt to compare with.")
                if ctsident and options.cleanup:
                    os.remove(ctsoutFile)
                    if os.path.isfile(newCtsout):
                        os.remove(newCtsout)
                else:
                    shutil.copy2(ctsoutFile, newCtsout)
                    #if options.diff:
                        #subprocess.call (["kdiff3",origCtsout,ctsoutFile])
            else:
                ctsret,ctsident = 0,True
            
            # output.txt (this output is required):
            if os.path.isfile(outputFile):
                origOutput = os.path.join(simDir,"expected/output%s.txt"%name)
                newOutput = os.path.join(simDir,"output%s.txt"%name)
                if os.path.isfile(origOutput):
                    ret,ident = compareOutput.main (origOutput, outputFile, 0)
                else:
                    ret,ident = 3,False
                    terminal.feed_command("\033[1;31mNo original output.txt to compare with.")
                if ident and options.cleanup:
                    os.remove(outputFile)
                    if os.path.isfile(newOutput):
                        os.remove(newOutput)
                else:
                    shutil.copy2(outputFile, newOutput)'''
        
        try:
            os.rmdir(simDir)
        except OSError:
            if success:
                terminal.feed_command("files are in Directory %s " % simDir +'\n\n')
        
        #terminal.feed_command("\033[0;00m")
        return success
