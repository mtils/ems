#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 10.05.2011

@author: michi
'''

from __future__ import print_function

import sys
import os.path
import sip
import argparse

from examples.qt4.bootstrap.create_app import create_app

def runModule(module):
    __import__(module)

def main(argv):

    parser = argparse.ArgumentParser(description='EMS Example-Runner')

    parser.add_argument('module', type=str, help='Run this Module',
                        default='')

    parser.add_argument('--env', type=str, help='Run in this environment',
                        default='testing')

    appPath = os.path.abspath(os.path.dirname(argv[0]))

    env = parser.parse_args().env

    app = create_app(argv, appPath, env=env)

    app.setQuitOnLastWindowClosed(True)

    runThisModule = parser.parse_args().module

    app.started += lambda app:__import__(runThisModule)

    sys.exit(app.start(appPath, argv))

if __name__ == "__main__":
    main(sys.argv)