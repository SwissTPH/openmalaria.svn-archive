#!/bin/sh
rm -rf out/*
javac -d class CombineSweeps.java && java -cp class -ea CombineSweeps in out --seeds 3

