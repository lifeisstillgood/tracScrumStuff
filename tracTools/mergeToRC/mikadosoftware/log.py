#!/usr/local/bin/python
#! -*- coding: utf-8 -*-

"""
Trying to define standard locations etc for logging  and errors

mikadosoftware/
 /log
 /error
 


"""

import logging
import os

GENERICLOGLOCATION='/tmp'

def getlogger(loghierarchy):
    ''' loghierarchy - something like mikadosoftware.trac 
    '''
    L = logging.Logger(loghierarchy)
    filepath = os.path.join(GENERICLOGLOCATION, loghierarchy + ".log")
    fh = logging.FileHandler(filepath)
    fmt = "%(asctime)s::%(levelname)s::%(pathname)s::%(lineno)d::%(message)s"
    fm = logging.Formatter(fmt)

    ### also output to console
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    # set a format which is simpler for console use
    formatter = logging.Formatter('%(levelname)-8s %(message)s')
    # tell the handler to use this format
    console.setFormatter(formatter)

    

    fh.setFormatter(fm)
    L.addHandler(fh)
    L.addHandler(console)
    return L

