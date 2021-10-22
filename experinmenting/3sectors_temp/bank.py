#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug  8 21:53:53 2021

@author: chengyu
"""
import abcEconomics as abce
import random
from utils import setup_custom_logger
logger = setup_custom_logger(__name__)
#from optimization_functions import optimization


class Bank(abce.Agent):
    def init(self, simulation_parameters):
        self.simulation_parameters = simulation_parameters
        self.policy_rate = 0.2
        self.create('money', 10e100)
        self.financial_account = {'outstanding_loan':0,
                                  'interest_payment':0,
                                  'bad_loan':0,
                                  }
        self.out_financial_account = str(self.financial_account)
        
    def update_policy_rate(self):
        ## dummy decistion function for testing purpose 
        self.policy_rate += self.time*0.00 ## increate 1 % by each round ; for testing only  
        
        ## to do: follow taylor rule
        # r = p + 0.5y + 0.5(p - 2) + 2
        # Where:
        # r = nominal fed funds rate
        # p = the rate of inflation
        # y = the percent deviation between current real GDP and the long-term linear trend in GDP 
        

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
            
            ## logger.info for debugging 
            if verbose:
                logger.info('send credit to firm id:{}; credit:{}'.format(m['firm_id'],m['amount']))
        
        #return None
    
    def log_balance_sheet(self,verbose=False):
        self.out_financial_account = str(self.financial_account)
        if verbose:
            logger.info('bank balance:{}'.format(self.financial_account))
            
    def return_public_info(self):
        
        res = {'Group':'Bank',
               'Id':self.id,
               'policy_rate': self.policy_rate}
        
        return res