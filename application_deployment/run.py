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

# With no arguments, run all scenario*.xml files.
# With arguments A,...,Z, only run scenarioA.xml, ..., scenarioZ.xml
# Exit status:
#	0 - all tests passed (or no tests)
#	1 - a test failed
#	-1 - unable to run test

import sys
import os
import tempfile
import glob
import time
import subprocess
import shutil
from optparse import OptionParser
import gzip
import re


base_folder = os.getcwd()
sys.path[0] = base_folder + "/application/common"
import compareOutput
import compareCtsout

testCommonDir = base_folder + "/application/common"
testSrcDir = base_folder + "/run_scenarios/scenarios_to_run"
testBuildDir = base_folder + "/application"
testOutputsDir = base_folder + "/run_scenarios/outputs"

if not os.path.isdir(testSrcDir) or not os.path.isdir(testBuildDir):
    print "Don't run this script directly; configure CMake then use the version in the CMake build dir."
    sys.exit(-1)
if not os.path.isfile (testCommonDir+"/scenario.xsd"):
    print "File not found (wrong CMake var?): " + testCommonDir +"/scenario.xsd"
    sys.exit(-1)

# executable
def findFile (*names):
    execs=set()
    for name in names:
        path=os.path.join(testBuildDir,name)
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

openMalariaExec=os.path.abspath(findFile (*["openMalaria","openMalaria.exe"]))

def linkOrCopy (src, dest):
    if hasattr(os, 'symlink'):
        os.symlink(os.path.abspath(src), dest)
    else:
        shutil.copy2(src, dest)

# Run, with file "scenario"+name+".xml"
def runScenario(options,omOptions,name):
    scenarioSrc=os.path.join(testSrcDir,"scenario%s.xml" % name)
     # since we use now absolute path we need now to adapt the path in the scenario file	
    src=open(scenarioSrc)
    scen_string=src.read()
    src.close()

    scenRE = re.compile('xsi:noNamespaceSchemaLocation="\s*"')
    scen_string = scenRE.sub('xsi:noNamespaceSchemaLocation='+testCommonDir+'/scenario.xsd', scen_string)
    
    dest= open(scenarioSrc, 'w')
    dest.write(scen_string)
    dest.close()	
    		
    if options.xmlValidate:
        # alternative: ["xmlstarlet","val","-s",SCHEMA,scenarioSrc]
        return subprocess.call (["xmllint","--noout","--schema " + testCommonDir + "/scenario.xsd",scenarioSrc],cwd=testBuildDir)
    
    cmd=options.wrapArgs+[openMalariaExec,"--resource-path",testCommonDir,"--scenario",scenarioSrc]+omOptions
    
    if not options.run:
        print "\033[0;32m  "+(" ".join(cmd))+"\033[0;00m"
        return 0
    
    # Run from a temporary directory, so checkpoint files won't conflict
    simDir = tempfile.mkdtemp(prefix=name+'-', dir=testOutputsDir)
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
    linkOrCopy (testCommonDir + "/scenario.xsd", scenario_xsd)
    
    if options.logging:
        print time.strftime("\033[0;33m%a, %d %b %Y %H:%M:%S")+"\t\033[1;33mscenario%s.xml" % name
    
    startTime=lastTime=time.time()
    # While no output.txt file and cmd exits successfully:	

    while (not os.path.isfile(outputFile)):
        if options.logging:
            print "\033[0;32m  "+(" ".join(cmd))+"\033[0;00m"
        #ret=subprocess.Popen(cmd, shell=False, cwd=simDir).pid
	ret=subprocess.call(cmd, shell=False, cwd=simDir)
        if ret != 0:
            print "\033[1;31mNon-zero exit status: " + str(ret)
            break
        
        # check for output.txt.gz in place of output.txt and uncompress:
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

    
    if options.livegraph:
	start = False
	while not(start):
		if(os.path.isfile(ctsoutFile)):	
			startLiveGraph(ctsoutFile, simDir)
			start = True 

    if ret == 0 and options.logging:
        print "\033[0;33mDone in " + str(time.time()-startTime) + " seconds"
    
    if options.cleanup:
        os.remove(scenario_xsd)
        for f in (glob.glob(os.path.join(simDir,"checkpoint*")) + glob.glob(os.path.join(simDir,"seed?")) + [os.path.join(simDir,"init_data.xml"),os.path.join(simDir,"boinc_finish_called"),os.path.join(simDir,"scenario.sum")]):
            if os.path.isfile(f):
                os.remove(f)
    
    # Compare outputs:
    if ret == 0:
        # ctsout.txt (this output is optional):
        if os.path.isfile(ctsoutFile):
            origCtsout = os.path.join(testOutputsDir,"expected/ctsout%s.txt"%name)
            newCtsout = os.path.join(testOutputsDir,"ctsout%s.txt"%name)
            if os.path.isfile(origCtsout):
                ctsret,ctsident = compareCtsout.main (origCtsout, ctsoutFile)
            else:
                ctsret,ctsident = 3,False
                print "\033[1;31mNo original ctsout.txt to compare with."
            if ctsident and options.cleanup:
                os.remove(ctsoutFile)
                if os.path.isfile(newCtsout):
                    os.remove(newCtsout)
            else:
                shutil.copy2(ctsoutFile, newCtsout)
                if options.diff:
                    subprocess.call (["kdiff3",origCtsout,ctsoutFile])
        else:
            ctsret,ctsident = 0,True
        
        # output.txt (this output is required):
        if os.path.isfile(outputFile):
            origOutput = os.path.join(testOutputsDir,"expected/output%s.txt"%name)
            newOutput = os.path.join(testOutputsDir,"output%s.txt"%name)
            if os.path.isfile(origOutput):
                ret,ident = compareOutput.main (origOutput, outputFile, 0)
            else:
                ret,ident = 3,False
                print "\033[1;31mNo original output.txt to compare with."
            if ident and options.cleanup:
                os.remove(outputFile)
                if os.path.isfile(newOutput):
                    os.remove(newOutput)
            else:
                shutil.copy2(outputFile, newOutput)
                if options.diff:
                    subprocess.call (["kdiff3",origOutput,outputFile])
        else:
            ret,ident = 1,False
            stderrFile=os.path.join(simDir,"stderr.txt")
            if os.path.isfile (stderrFile):
                print "\033[1;31mNo output 'output.txt'; error messages:"
                se = open(stderrFile)
                se.read()
                se.close()
            else:
                print "\033[1;31mNo output 'output.txt'"
        
        ret=max(ret,ctsret)
        ident=ident and ctsident
    
    try:
        os.rmdir(simDir)
    except OSError:
        print "\033[0;31mDirectory %s not empty, so not deleted!" % simDir
    
    print "\033[0;00m"
    return ret

def setWrapArgs(option, opt_str, value, parser, *args, **kwargs):
    parser.values.wrapArgs = args[0]

# Test for options
def evalOptions (args):
    parser = OptionParser(usage="Usage: %prog [options] [-- openMalaria options] [scenarios]",
			description="""Scenarios to be run must be of the form scenarioXX.xml; if any are passed on the command line, XX is substituted for each given; if not then all files of the form scenario*.xml are run as test scenarios.
You can pass options to openMalaria by first specifying -- (to end options passed from the script); for example: %prog 5 -- --print-model""")
    
    parser.add_option("-q","--quiet",
		    action="store_false", dest="logging", default=True,
		    help="Turn off console output from this script")
    parser.add_option("-n","--dry-run", action="store_false", dest="run", default=True,
		    help="Don't actually run openMalaria, just output the commandline.")
    parser.add_option("-c","--dont-cleanup", action="store_false", dest="cleanup", default=True,
		    help="Don't clean up expected files from the temparary dir (checkpoint files, schema, etc.)")
    parser.add_option("-d","--diff", action="store_true", dest="diff", default=False,
            help="Launch a diff program (kdiff3) on the output if validation fails")
    parser.add_option("--valid","--validate",
		    action="store_true", dest="xmlValidate", default=False,
		    help="Validate the XML file(s) using xmllint and the latest schema.")
    parser.add_option("-t", "--translateSchema", "--translate", action="store_true", dest="translator", default=False,
    		    help="Use the Schema Translating tool in application/schemaTranslator/schemaTranslator/.")
    parser.add_option("-l","--liveGraph","--graph", action="store_true", dest="livegraph", default=False, 
		    help="Use the Live Graph application to output the simulation (a ctsout file is needed, otherwise you will see nothing).") 		
    (options, others) = parser.parse_args(args=args)
    options.ensure_value("wrapArgs", [])
    
    toRun=set()
    omOptions=[]
    for arg in others:
        if (arg[0] == '-'):
            omOptions = omOptions + [arg]
        else:
            toRun.add (arg)
    
    return options,omOptions,toRun

def startSchemaTranslator():
	return subprocess.call ("java -classpath "+testBuildDir+"/schemaTranslator SchemaTranslator --schema_folder "+testCommonDir+"/", shell=True)

def startLiveGraph(ctsoutpath, simPath):
	settings_path = testCommonDir + "/settings.lgdfs"
	src=open(settings_path)
    	settings_string=src.read()
    	src.close()

    	settingsRE = re.compile('changeEntry')
    	settings_string = settingsRE.sub(ctsoutpath, settings_string)
    
    	dest= open(simPath+"/settings.lgdfs", 'w')
    	dest.write(settings_string)
    	dest.close()
	
	return subprocess.Popen ("java -jar "+testBuildDir+"/LiveGraph.1.14.Complete/LiveGraph.1.14.Complete.jar -dfs "+simPath+"/settings.lgdfs", shell=True).pid	


def main(args):
    (options,omOptions,toRun) = evalOptions (args[1:])
    retVal = 0
	 

    if not(options.translator):	
	if not toRun:
		for p in glob.iglob(os.path.join(testSrcDir,"scenario*.xml")):
	    		f = os.path.basename(p)
	    		n=f[8:-4]
	    		assert ("scenario%s.xml" % n) == f
	    		toRun.add(n)

	for name in toRun:
		r=runScenario(options,omOptions,name)
		retVal = r if retVal == 0 else retVal
    else:
	retVal = startSchemaTranslator()

    return retVal

if __name__ == "__main__":
    sys.exit(main(sys.argv))
