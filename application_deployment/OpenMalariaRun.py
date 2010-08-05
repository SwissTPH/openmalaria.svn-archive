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


from VirtualTerminal import VirtualTerminal
from JavaAppsRun import LiveGraphRun
from datetime import date

class OpenMalariaRun():
    
    base_folder = os.getcwd()
    sys.path[0] = base_folder + "/application/common"
    import compareOutput
    import compareCtsout
    
    testCommonDir = base_folder + "/application/common"
    testSrcDir = base_folder + "/run_scenarios/scenarios_to_run"
    testBuildDir = base_folder + "/application"
    testOutputsDir = base_folder + "/run_scenarios/outputs"
    testTranslationDir = base_folder + "/translate_scenarios"
    testTranslationDirIn = testTranslationDir + "/scenarios_to_translate"
    testTranslationDirOut = testTranslationDir + "/translated_scenarios"
    
    
    
    
    # executable
    def findFile (self, *names):
        
        execs=set()
        for name in names:
            path=os.path.join(os.getcwd()+"/application",name)
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
    
    # Run, with file "scenario"+name+".xml"
    def runScenario(self, terminal, livegraph, path, name, checkpointing=False, nocleanup=False, runLiveGraph=False):
        
        scenarioSrc = path
        simDir= self.testOutputsDir+"/"+name+"_"+time.strftime("%d_%b_%Y_%H%M%S")
        openMalariaExec=os.path.abspath(self.findFile (*["openMalaria","openMalaria.exe"]))
        
        cmd= openMalariaExec+" --resource-path "+self.testCommonDir+" --scenario "+scenarioSrc
        if(checkpointing):
            cmd = cmd+' --checkpoint'
        
        os.mkdir(simDir)
        shutil.copy2(scenarioSrc, simDir)
        
        outputFile=os.path.join(simDir,"output.txt")
        outputGzFile=os.path.join(simDir,"output.txt.gz")
        ctsoutFile=os.path.join(simDir,"ctsout.txt")
        ctsoutGzFile=os.path.join(simDir,"ctsout.txt.gz")
        checkFile=os.path.join(simDir,"checkpoint")	
        
        # Link or copy required files.
        # The schema file only needs to be copied in BOINC mode, since otherwise the
        # scenario is opened with a path and the schema can be found in the same
        # directory. We copy it anyway.
        scenario_xsd=os.path.join(simDir,"scenario.xsd")
        self.linkOrCopy (self.testCommonDir + "/scenario.xsd", scenario_xsd)
        
        terminal.feed_command(time.strftime("\033[0;33m%a, %d %b %Y %H:%M:%S")+"\t\033[1;33m%s.xml" % name)
        startTime=lastTime=time.time()
    
        while (not os.path.isfile(outputFile)):
            terminal.feed_command("\033[0;32m  "+cmd+"\033[0;00m")
            terminal.run_openmalaria_command(cmd, simDir, livegraph, ctsoutFile, runLiveGraph)
            
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
    
        terminal.feed_command("\033[0;33mDone in " + str(time.time()-startTime) + " seconds")
        
        if not nocleanup:
            os.remove(scenario_xsd)
            for f in (glob.glob(os.path.join(simDir,"checkpoint*")) + glob.glob(os.path.join(simDir,"seed?")) + [os.path.join(simDir,"init_data.xml"),os.path.join(simDir,"boinc_finish_called"),os.path.join(simDir,"scenario.sum")]):
                if os.path.isfile(f):
                    os.remove(f)
        
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
            terminal.feed_command("\033[0;31m files are in Directory %s " % simDir)
        
        terminal.feed_command("\033[0;00m")
        return simDir
