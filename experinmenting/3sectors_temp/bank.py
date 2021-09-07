#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug  8 21:53:53 2021

@author: chengyu
"""
import abcEconomics as abce
import random
#from optimization_functions import optimization


class Bank(abce.Agent):
    def init(self, simulation_parameters):
        self.simulation_parameters = simulation_parameters
        self.interest_rate = 0.02
        self.financial_account = {}
        

    def distribute_credit(self):
        msgs = self.get_messages('purchase_order')
        
        
        
        
        
        return None