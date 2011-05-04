#!/bin/bash

# ** should match all files in sub-directories
shopt -s globstar
for f in **/*.java; do
	CF="$(dirname $f)/$(basename $f .java).class"
	echo $CF
	if [ -e $CF ]; then
		if [ $f -nt $CF ]; then
			javac $f
		fi
	else
		javac $f
	fi
done

