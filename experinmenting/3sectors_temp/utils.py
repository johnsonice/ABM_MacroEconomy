#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 16 09:54:15 2021

@author: chengyu
"""

import logging
import random
import pandas as pd 
import ast
import glob
import os.path


#%%
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
        
def get_current_res_folder(folder='./result'):
    patten = folder+'/*' ## get everything
    all_files = glob.glob(patten)
    max_fol = max(all_files, key=os.path.getctime)
    return max_fol
    
def print_random():
    print(random.normalvariate(0,0.1))

