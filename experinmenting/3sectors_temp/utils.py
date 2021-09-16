#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 16 09:54:15 2021

@author: chengyu
"""

import logging

def setup_custom_logger(name):
    #formatter = logging.Formatter(fmt='%(asctime)s %(message)s')
    logging.basicConfig(format='%(levelname)s - %(name)s:  %(message)s')
    
    # handler = logging.StreamHandler()
    # handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    #logger.addHandler(handler)
    
    return logger

def clean_and_refill_firms(d_firms,firms,logger):
    dfs = [i for i in d_firms[0] if i is not None]
    if len(dfs)>0:
        firms.delete_agents(dfs)
        logger.info("Delete frims: {}".format(dfs))
    else:
        pass
        #logger.info('no frims dropped out this round')
        

def chang_x(x):
    x.append(1)
    
    