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
        self.create('money', 1000000)
        self.financial_account = {'total_loan':0,
                                  'interest_payment':0,
                                  'bad_loan':0}
        

    def distribute_credit(self,verbose=False):
        msgs = self.get_messages('corporate_debt')
        for m in msgs:
            self.send(('firm',m['firm_id']),'corporate_credit',{'amount':m['amount']})
            self.give(('firm',m['firm_id']),good='money',quantity=m['amount'])
        
            if verbose:
                print('send credit to firm id:{}; credit:{}'.format(m['firm_id'],m['amount']))
        
        return None