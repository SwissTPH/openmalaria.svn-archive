#!/usr/bin/python
# -*- coding: utf-8 -*-
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
from optparse import OptionParser

sys.path[0]="@CMAKE_CURRENT_SOURCE_DIR@"
import compareOutputsFloat as compareOuts

# replaced by CMake; run the version it puts in the build/test/ dir.
testSrcDir="@CMAKE_CURRENT_SOURCE_DIR@"
testBuildDir="@CMAKE_CURRENT_BINARY_DIR@"
if testSrcDir[0] == '@':
  print "Don't run this script directly; configure CMake then use the version in the CMake build dir."
  sys.exit(-1)

# executable
openMalariaExec=os.path.join(testBuildDir,"../openMalaria")
if not os.access(openMalariaExec, os.X_OK):
  openMalariaExec = openMalariaExec + ".exe"
  if not os.access(openMalariaExec, os.X_OK):
    print "Unable to find: openMalaria[.exe]; please compile it."
    sys.exit(-1)

def linkOrCopy (src, dest):
  if hasattr(os, 'symlink'):
    os.symlink(os.path.abspath(src), dest)
  else:
    shutil.copy2(src, dest)

# Run, with file "scenario"+name+".xml"
def runScenario(options,omOptions,name):
  if options.xmlValidate:
    return subprocess.call ("xmllint --noout --schema @OMTEST_SCEMA_NAME@",
			 cwd=simDir)
  
  cmd=options.wrapArgs+[openMalariaExec,"--scenario",os.path.join(testSrcDir,"scenario%s.xml" % name)]+omOptions
  
  if not options.run:
    print "\033[1;32m",cmd,"\033[0;00m"
    return
  
  # Run from a temporary directory, so checkpoint files won't conflict
  simDir = tempfile.mkdtemp(prefix='temp', dir=testBuildDir)
  outFile=os.path.join(simDir,"output.txt")
  outNameFile=os.path.join(testBuildDir,"output"+name+".txt")
  if (os.path.isfile(outNameFile)):
    os.remove (outNameFile)
  checkFile=os.path.join(simDir,"checkpoint")
  
  # Link or copy required files.
  densities_csv=os.path.join(simDir,"densities.csv")
  scenario_xsd=os.path.join(simDir,"@OMTEST_SCEMA_NAME@")
  linkOrCopy (os.path.join(testSrcDir,"densities.csv"), densities_csv)
  linkOrCopy (os.path.join(testSrcDir,"@OMTEST_SCEMA_NAME@"), scenario_xsd)
  # Note: name may not always be correct; scan scenario XML file if you really want to be sure!
  Nv0fileSrc=os.path.join(testSrcDir,"Nv0scenario{0}.txt".format(name))
  Nv0file=os.path.join(simDir,"Nv0scenario{0}.txt".format(name))
  if os.path.isfile(Nv0fileSrc):
    linkOrCopy (Nv0fileSrc,Nv0file)
  
  if options.logging:
    print time.strftime("\033[0;33m%a, %d %b %Y %H:%M:%S")
  
  lastTime=time.time()
  # While no output and cmd exits successfully:
  while (not os.path.isfile(outFile)):
    if options.logging:
      print "\033[1;32m",cmd,"\033[0;00m"
    ret=subprocess.call (cmd, shell=False, cwd=simDir)
    if ret:
      print "Non-zero exit status: {}".format(ret)
      break
    
    # if the checkpoint file hasn't been updated, stop
    if not os.path.isfile(checkFile):
      break
    checkTime=os.path.getmtime(checkFile)
    if not checkTime > lastTime:
      break
    lastTime=checkTime
  
  stderrFile=os.path.join(simDir,"stderr.txt")
  if os.path.isfile(stderrFile):
    dest=os.path.join(testBuildDir,"stderr.txt")
    os.rename(stderrFile,dest)
    stderrFile=dest
  
  os.remove(densities_csv)
  os.remove(scenario_xsd)
  if os.path.isfile(Nv0file):
    os.remove (Nv0file)
  if os.path.isfile(outFile):
    os.rename(outFile,outNameFile)
  
  try:
    os.rmdir(simDir)
  except OSError:
    print "Directory %s not empty, so not deleted!" % simDir
  
  if os.path.isfile(outNameFile):
    print "\033[1;34m",
    return compareOuts.main (*["",os.path.join(testSrcDir,"original%s.txt"%name), outNameFile, 1])
  else:
    if os.path.isfile (stderrFile):
      print "\033[0;31mNo results output; error messages:"
      se = file.open(stderrFile)
      se.read()
      se.close()
    else:
      print "\033[0;31mNo results output; error messages:"
  print "\033[0;00m"
  return 1

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
  parser.add_option("--valid","--validate",
		    action="store_true", dest="xmlValidate", default=False,
		    help="Validate the XML file(s) using xmllint and the latest schema.")
  parser.add_option("-g","--gdb", action="callback", callback=setWrapArgs,
		    callback_args=(["gdb","--args"],),
		    help="Run openMalaria through gdb.")
  parser.add_option("--valgrind", action="callback", callback=setWrapArgs,
		    callback_args=(["valgrind","--gen-suppressions=yes","leak-check=full"],),
		    help="Run openMalaria through valgrind.")
  parser.add_option("--valgrind-track-origins", action="callback", callback=setWrapArgs,
		    callback_args=(["valgrind","--gen-suppressions=yes","leak-check=full","--track-origins=yes"],),
		    help="As --valgrind, but pass --track-origins=yes option (1/2 performance).")
  parser.add_option("-n","--dry-run", action="store_false", dest="run", default=True,
		    help="Don't actually run openMalaria, just output the commandline.")
  (options, others) = parser.parse_args(args=args)
  
  options.ensure_value("wrapArgs", [])
  
  toRun=set()
  omOptions=[]
  for arg in others:
    if (arg[0:2] == "--"):
      omOptions = omOptions + [arg]
    else:
      toRun.add (arg)
  
  return options,omOptions,toRun


def main(args):
  (options,omOptions,toRun) = evalOptions (args[1:])
  
  if not toRun:
    for p in glob.iglob(os.path.join(testSrcDir,"scenario*.xml")):
      f = os.path.basename(p)
      n=f[8:-4]
      assert ("scenario%s.xml" % n) == f
      toRun.add(n)
  
  retVal=0
  for name in toRun:
    r=runScenario(options,omOptions,name)
    retVal = r if retVal == 0 else retVal
  
  return retVal

if __name__ == "__main__":
  sys.exit(main(sys.argv))
