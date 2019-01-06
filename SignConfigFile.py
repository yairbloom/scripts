#!/usr/bin/python
######################################################################
#  Use this file to sign a configuration file after manual editing.
#
#  Dov Grobgeld
#  2016-05-05 Thu
######################################################################

import os
import sys
Application="/work/MetalJet/XjetApps/MetalJet/Apps/Project/qt/"
sys.path.insert(0, Application + "Lib")

import ConfigurationUtils
import argparse

parser = argparse.ArgumentParser(
  description='Sign a configuration file after manual editing.')

parser.add_argument('Filename')

Args = parser.parse_args()

ConfigurationUtils.SignConfiguration(Args.Filename)

