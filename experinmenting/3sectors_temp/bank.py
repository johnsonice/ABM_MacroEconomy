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
        self.policy_rate = 0.03
        self.create('money', 1000000)
        self.financial_account = {'outstanding_loan':0,
                                  'interest_payment':0,
                                  'bad_loan':0,
                                  }
    def update_policy_rate(self):
        ## dummy decistion function for testing purpose 
        self.policy_rate += self.time*0.01 ## increate 1 % by each round ; for testing only  
        
        

    def collect_payment(self):
        msgs = self.get_messages('debt_payment')
        for m in msgs:
            self.financial_account['outstanding_loan'] -= m['principle_payment']
            self.financial_account['interest_payment'] += m['interest_payment']
        
        bl_msgs = self.get_messages('bad_loan')
        for m in bl_msgs:
            self.financial_account['outstanding_loan'] -= m['amount']
            self.financial_account['bad_loan'] += m['amount']

        #return None

    def distribute_credit(self,verbose=False):
        msgs = self.get_messages('corporate_debt')
        for m in msgs:
            self.send(('firm',m['firm_id']),'corporate_credit',{'amount':m['amount']})
            self.give(('firm',m['firm_id']),good='money',quantity=m['amount'])
            
            ## record load 
            self.financial_account['outstanding_loan'] += m['amount']
            
            ## print for debugging 
            if verbose:
                print('send credit to firm id:{}; credit:{}'.format(m['firm_id'],m['amount']))
        
        #return None
    
    def log_balance_sheet(self,verbose=False):
        if verbose:
            print('bank balance:{}'.format(self.financial_account))
            
    def return_public_info(self):
        
        res = {'Group':'Bank',
               'Id':self.id,
               'policy_rate': self.policy_rate}
        
        return res