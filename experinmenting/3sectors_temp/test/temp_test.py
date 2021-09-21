#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 17 11:17:21 2021

@author: chengyu
"""

""" 

Most basic 2 sector model, Firms hire random households for labor, produce consumption good and sell to ramdom households, 
House earn wage from selling their laobr, buys comsumer goods and accumulate utility

"""
from abcEconomics import Simulation
from firm import Firm
from household import Household
from bank import Bank
import config
from utils import setup_custom_logger,clean_and_refill_firms
import random
import numpy as np
random.seed(1)
np.random.seed(1)
from utils import print_random

logger = setup_custom_logger('main')

#%%
w = Simulation(processes=1,random_seed = 1) ## set to 1 for debugging purpose 

firms = w.build_agents(Firm, 'firm', config.simulation_parameters['n_firms'], simulation_parameters = config.simulation_parameters)
households = w.build_agents(Household, 'household', config.simulation_parameters['n_households'],simulation_parameters = config.simulation_parameters)
banks = w.build_agents(Bank, 'bank', config.simulation_parameters['n_banks'],simulation_parameters = config.simulation_parameters)

#%%
for r in range(config.simulation_parameters['rounds']):
    w.advance_round(r)
    logger.info('itetration:{}'.format(w.time))
    print_random()
    firms.debug()
    
w.finalize()


# if __name__ == '__main__':
    #main(simulation_parameters)
