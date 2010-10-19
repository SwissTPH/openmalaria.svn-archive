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
import string
import math
import unittest
from optparse import OptionParser
from approxEqual import ApproxEqual

REL_PRECISION=1e-6
ABS_PRECISION=1e-6

class ValIdentifier:
    def __init__(self,s,g,m):
        self.survey = s
        self.group = g
        self.measure = m
    def __eq__(self,other):
        return (self.survey == other.survey) and (self.group == other.group) and (self.measure == other.measure)
    def __hash__(self):
        return self.survey.__hash__() ^ self.group.__hash__() ^ self.measure.__hash__()

class TestValIdentifier (unittest.TestCase):
    def setUp(self):
        self.a1 = ValIdentifier(2,4,0);
        self.a2 = ValIdentifier(2,4,0);
        self.a3 = ValIdentifier(2,2,0);
        self.b1 = ValIdentifier(0,"abc",5);
        self.b2 = ValIdentifier(0,"abc",5);
    def testEq (self):
        self.assert_ (self.a1.survey == self.a2.survey)
        self.assert_ (self.a1 == self.a2)
        self.assert_ (self.b1 == self.b2)
        self.assert_ (self.a1 != self.a3)
    def testHash (self):
        self.assert_ (self.a1.__hash__ == self.a2.__hash__)
        self.assert_ (self.a1.__hash__ != self.a3.__hash__) # actually, could sometimes be
        self.assert_ (self.b1.__hash__ == self.b2.__hash__)


def charEqual (fn1,fn2):
    MAX=10*1024
    f1 = open(fn1,'r')
    f2 = open(fn2,'r')
    while True:
        s1 = f1.read(MAX)
        s2 = f2.read(MAX)
        if (len(s1)==0) or (len(s2)==0):
            # end of one or both files; equal if it's the end of both
            return len(s1) == len(s2)
        if s1 != s2:
            return False

#http://stackoverflow.com/questions/2974124/reading-floating-point-numbers-with-1-qnan-values-in-python
def robust_float(s):
    try:
        return float(s)
    except ValueError:
        if 'nan' in s.lower():
            return 1e1000-1e1000 # NaN
        else:
            raise

def ReadEntries (fname):
    values=dict()
    fileObj = open(fname, 'r')
    for line in fileObj:
        items=string.split(line)
        if (len(items) != 4):
            print "expected 4 items on line; found (following line):"
            print line
            continue
            
        key=ValIdentifier(int(items[0]),items[1],int(items[2]))
        values[key]=robust_float(items[3])
    return values

def main(fn1,fn2,maxDiffsToPrint=6):
    """Takes names of the two files to compare and optionally an argument describing
the maximum number of differences to print directly (note: order is not intuitive).
Returns a tuple ret,ident; ret is 0 if test passes (output considered near-enough equal),
ident is 1 if files are binary-equal."""
    ret=0
    opt=""
    if REL_PRECISION!=1e-6:
        opt+=" --rel-prescision="+str(REL_PRECISION)
    if ABS_PRECISION!=1e-6:
        opt+=" --abs-prescision="+str(ABS_PRECISION)
    print "\033[1;34m  compareOutput.py"+opt+" "+fn1+" "+fn2+" "+str(maxDiffsToPrint)+"\033[0;0m"
    
    # Read both files and combine into a map of key to pairs (v1, v2)
    try:
        if charEqual (fn1,fn2):
            print "output.txt files are identical"
            return 0,True
        print "output.txt files aren't binary-equal"
        
        values1=ReadEntries(fn1)
        values2=ReadEntries(fn2)
    # python 3000 syntax is "except IOError as e", backported to 2.6 but not always supported. Old syntax:
    except IOError, e:
        print str(e)
        return 1,False
    values=dict()
    for (k,v1) in values1.iteritems():
        v2=None
        if (k in values2):
            v2=values2[k]
            del values2[k]
        values[k] = (v1,v2)
    for (k,v2) in values2.iteritems():
        values[k] = (None,v2)
    
    # Go through all values:
    numPrinted=0
    numDiffs=0
    numMissing1=0
    numMissing2=0
    perMeasureNum = dict()
    perMeasureTotal1 = dict()
    perMeasureTotal2 = dict()
    perMeasureNumDiff = dict()
    perMeasureDiffSum = dict()
    perMeasureDiffAbsSum = dict()
    approxEqual = ApproxEqual(REL_PRECISION, ABS_PRECISION)
    
    for (k,(v1,v2)) in values.iteritems():
        if v1==None:
            numMissing1 += 1
        elif v2==None:
            numMissing2 += 1
        else:
            perMeasureNum[k.measure] = perMeasureNum.get(k.measure, 0) + 1
            perMeasureTotal1[k.measure] = perMeasureTotal1.get(k.measure, 0.0) + v1
            perMeasureTotal2[k.measure] = perMeasureTotal2.get(k.measure, 0.0) + v2
            
            # Compare with relative precision
            if approxEqual (v1, v2):
                continue
            
            numDiffs += 1
            # Sum up total difference per measure
            perMeasureDiffSum[k.measure]    = perMeasureDiffSum.get(k.measure,0.0)    + v2 - v1
            perMeasureDiffAbsSum[k.measure] = perMeasureDiffAbsSum.get(k.measure,0.0) + math.fabs(v2-v1)
        
        numPrinted += 1
        perMeasureNumDiff[k.measure] = perMeasureNumDiff.get(k.measure,0) + 1;
        if (numPrinted <= maxDiffsToPrint):
            print "survey "+str(k.survey)+", group "+str(k.group)+", measure "+str(k.measure)+": "+str(v1)+" -> "+str(v2)
            if (numPrinted == maxDiffsToPrint):
                print "[won't print any more line-by-line diffs]"
    
    if (numMissing1 > 0) or (numMissing2 > 0):
        print str(numMissing1) + " entries missing from first file, " + str(numMissing2) +" from second"
        ret = 3
    
    for (k.measure,absDiff) in perMeasureDiffAbsSum.iteritems():
        if not (absDiff <= 1e-6):   # handle NANs
            # standard division throws on divide-by-zero, which I don't want
            def div(x,y):
                try:
                    return x/y
                except ZeroDivisionError:
                    return 1e400 * 0 # nan
            
            diff=perMeasureDiffSum[k.measure]
            sum1=perMeasureTotal1[k.measure]
            sum2=perMeasureTotal2[k.measure]
            print "for measure "+str(k.measure)+":\tsum(1st file):"+str(sum1)+"\tsum(2nd file):"+str(sum2)+"\tdiff/sum: "+str(div(diff,sum1))+"\t(abs diff)/sum: "+str(div(absDiff,sum1))
    
    # We print total relative diff here: 1.0 should mean roughly, one parameter is twice what it should be.
    if numDiffs == 0:
        print "No significant differences (total relative diff: "+str(approxEqual.totalRelDiff/1.e6)+"), ok..."
        return ret,False
    else:
        print "\033[1;31m"+str(numDiffs)+" significant differences (total relative diff: "+str(approxEqual.totalRelDiff/1.e6)+ ")!\033[0;0m"
        return 1,False

# Test for options
def evalOptions (args):
    parser = OptionParser(usage="Usage: %prog [options] logfile1 logfile2 [max different lines to print]",
            description="""Scenarios to be run must be of the form scenarioXX.xml; if any are passed on the command line, XX is substituted for each given; if not then all files of the form scenario*.xml are run as test scenarios.
You can pass options to openMalaria by first specifying -- (to end options passed from the script); for example: %prog 5 -- --print-model""")
    
    parser.add_option("-R","--rel-precision",
            action="store", dest="rel_precision", type="float",
            help="Set relative precision (default: 1.0e-6)")
    parser.add_option("-A","--abs-precision",
            action="store", dest="abs_precision", type="float",
            help="Set absolute precision (default: 1.0e-6)")
    (options, others) = parser.parse_args(args=args)
    
    return options,others

if __name__ == '__main__':
    #uncomment to run unittests:
    #unittest.main()
    
    (options,others) = evalOptions (sys.argv[1:])
    if options.rel_precision:
        REL_PRECISION=options.rel_precision
    if options.abs_precision:
        ABS_PRECISION=options.abs_precision
    
    if (len(others) == 3):
        ret,ident = main (others[0],others[1],int(others[2]))
    elif (len(others) == 2):
        ret,ident = main (others[0],others[1])
    else:
        print "Usage: "+sys.argv[0]+" logfile1 logfile2 [max different lines to print]"
        ret=-1
    sys.exit(ret)
