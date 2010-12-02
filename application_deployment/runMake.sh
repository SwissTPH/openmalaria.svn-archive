#!/bin/bash

cxfreeze start_gui.py --install-dir ./ --include-modules cairo,pango,pangocairo,gio,atk,encodings.utf_8
cp start_gui openmalariatools 
