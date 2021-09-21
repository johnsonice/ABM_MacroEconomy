import abcEconomics as abce
import random
import math
import logging
import copy
import pandas as pd
from utils import setup_custom_logger
logger = setup_custom_logger(__name__)


class Firm(abce.Agent, abce.Firm):
    def init(self,simulation_parameters):
        """ there are now 2 sectors:
        - upstream produces an intermediary good
        - downstream uses labor and the intermediary good to produce the final good

        there is an initial endowment to avoid bootstrapping problems
        """
        self.simulation_parameters = simulation_parameters
        self.create('money', 20)
        self.create('consumption_good', 1)                                                             ## initiate with one good 
        self.inputs = {"labor": 1}
        self.output = "consumption_good"      
        self.cobb_douglas_multiplier = 5
        # self.price = {'consumption_good':1,
        #               'labor':3}
        self.cash_buffer = 10                   ## when cash balance below that, will request for credit
        # self._inventory._perishable.append('labor') 
        # self._inventory._perishable.append('consumption_good') 
        self.checkorders = []
        self.pf = self.create_cobb_douglas(self.output, self.cobb_douglas_multiplier, self.inputs)     ## need to understand this a bit more 
        self.balance_sheet = {'money':self.not_reserved('money'),
                              'consumption_good':None,
                              'debt':0}
        self.iter_memory_current ={'iter':0,
                                   'solvency_status': True,
                                   'planned_production': 10,                                            ## very random, default to 4 for now
                                   'labor_needed': 2,
                                   'actual_production':None,
                                   'new_credit_received':0,
                                   'balance_sheet':self.balance_sheet,
                                   'market_interest':0.02,
                                   'amortization_rate':0.05,
                                   'price_consumption_good':2 + random.normalvariate(0,0.1),
                                   'price_labor':5,
                                   'labor_hired':[],
                                   'goods_sold':[]}
        self.out_iter_memory_current = str(self.iter_memory_current)
        self.iter_memory_history = []
        
    #################################
    #### Financial Market Open ###### 
    #################################
    def debug(self):
        logger.info("{},{}".format(self.id,random.normalvariate(1,0.2)))
    
    def receive_policy_rate_info(self,info):
        self.iter_memory_current['market_interest']=info[0][0]['policy_rate']
    
    
    def check_financial_viability(self,verbose=False):
        """
        check sovency status, payback bank, delete/refill agent 
        """
        
        #logger.info(self.id,self.possessions())
        #logger.info(self.id,self.iter_memory_current['balance_sheet']['debt'],self.iter_memory_current['market_interest'])
        
        interest_payment = self.balance_sheet['debt'] * self.iter_memory_current['market_interest'] 
        principle_payment = self.balance_sheet['debt'] * self.iter_memory_current['amortization_rate']
        debt_service = interest_payment + principle_payment
        solvency_status = self.balance_sheet['money'] >= debt_service
        self.iter_memory_current['solvency_status'] = solvency_status
        
        if solvency_status == True:
            ## send money and message to bank 
            self.give(('bank',0),'money',debt_service)
            self.send(('bank',0),'debt_payment',{'interest_payment':interest_payment,
                                                 'principle_payment': principle_payment})
            ## update balance
            self.balance_sheet['money'] = self.not_reserved('money')
            self.balance_sheet['debt']-= principle_payment
            
            if verbose:
                logger.info('market interest : {}; Send {} to bank'.format(self.iter_memory_current['market_interest'],debt_service))
                
            return None
        
        else:
            ## Firm default / liquidate all assets 
            self.give(('bank',0),'money',self.not_reserved('money'))
            ## calculate bad loand amount 
            bad_loan = self.balance_sheet['debt']+interest_payment - self.not_reserved('money')
            self.send(('bank',0),'bad_loan',{'amount':bad_loan})
            
            if verbose:
                logger.info('market interest : {}; Send {} to bank; Firm default'.format(self.iter_memory_current['market_interest'],
                                                                                         self.not_reserved('money')))
            
            ## return id for deletion 
            return 'firm',self.id
         
        
    
    def plan_production(self,verbose=False,Q=None):
        """
        to be implemented; 
        based on historical data, determine current production/ needed inputs / price
        -- current version is a very nieve version, will need to be changd latter 
        """
        ## a naive production adjustment 
        if self.balance_sheet['consumption_good'] is None or self.iter_memory_current['actual_production'] is None:
            pass        
        
        elif self.balance_sheet['consumption_good'] == 0 :
            self.iter_memory_current['planned_production'] = math.ceil(self.iter_memory_current['planned_production']*1.1)  ## increase by 20%
            self.iter_memory_current['price_consumption_good'] *= 1.1 
            
        elif self.balance_sheet['consumption_good'] > 0:
            self.iter_memory_current['planned_production'] = math.ceil(self.iter_memory_current['actual_production']*0.9)  ## shrink production based on inventory
            self.iter_memory_current['price_consumption_good'] *= 0.9 
        
        ## updated label needed 
        self.iter_memory_current['labor_needed'] = math.ceil(self.iter_memory_current['planned_production']/self.cobb_douglas_multiplier)
        
        if verbose:
            ## logger.info info for debugging
            logger.info('id:{}; previous inventory:{}; planned production:{}; labor needed:{}'.format(self.id,
                                                                                                self.iter_memory_current['balance_sheet']['consumption_good'],
                                                                                                self.iter_memory_current['planned_production'],
                                                                                                self.iter_memory_current['labor_needed']))
        
        return self.iter_memory_current['planned_production']
        
    
    def request_credit(self,verbose=False):
        needed_resource = self.iter_memory_current['labor_needed']*self.iter_memory_current['price_labor']
        credit_needed = needed_resource - (self.not_reserved('money') - self.cash_buffer)
        if credit_needed>0:
            ## request for credit 
            self.send(('bank',0),'corporate_debt',{'firm_id':self.id,
                                                   'amount':credit_needed,
                                                    })
        else:
            credit_needed = 0 
            
        if verbose:
            logger.info('id:{}; credit needed:{}'.format(self.id,credit_needed))
        
        return self.id,credit_needed
        
    def record_debt(self):
        ## update balance sheet
        msgs = self.get_messages('corporate_credit')
        for m in msgs:
            self.balance_sheet['debt'] += m['amount']
            self.iter_memory_current['new_credit_received']+=m['amount']
            
        return None
        
    def filter_applications_and_send_offer(self,n_hires=5,verbose=False):
        """
        send out conditional offer to qualified candidates
        
        Parameters
        ----------
        n_hires : int, optional
            DESCRIPTION. The default is 5.
            number of employees firm would like to hire in this iteration 
        Returns
        -------
        None
        """
        #logger.info(self.group, self.id)
        num_hired = self.not_reserved('labor')
        n_hires = self.iter_memory_current['labor_needed']
        
        
        if num_hired < n_hires:  ## check if we hired enough, if not look though offers
            msgs = self.get_messages('application')
            sorted_applications = sorted(msgs, key=lambda k: k['price']) 
            
            if verbose:
                logger.info('--- firm id:{}; sorted application: {}'.format(self.id,sorted_applications[:int(n_hires-num_hired) ]))
            
            n_openings = n_hires - num_hired        ## get remaining opeining positions 
            for idx,application in enumerate(sorted_applications[:n_hires]):
                if idx < n_openings:                 ## make sure we don exceed max hiring positions 
                    self.send(('household',application['household_id']),'conditional_offer',{'firm_id':self.id,
                                                                                             'salary':application['price']*random.normalvariate(1.1,0.1)})
        else:
            ## else do nothing 
            pass
        
    def buy_inputs(self,verbose=False):
        oo = self.get_offers("labor")
        for offer in oo:
            order = self.accept(offer,min(offer.quantity,
                                   math.floor(self.not_reserved('money')/offer.price)))
            if order is not None:
                self.iter_memory_current['labor_hired'].append(order) 
            
        if verbose:
            logger.info('id:{}; labor hired {}'.format(self.id,self.possessions()['labor']))

    def production(self):
        available_inputs = self.not_reserved('labor')
        prod_inputs = {'labor':available_inputs}
        if available_inputs>0:
            #self.produce_use_everything()
            output = self.produce(self.pf, prod_inputs)
        
        ## update iter memory 
        self.iter_memory_current['actual_production'] = available_inputs * self.cobb_douglas_multiplier
        

    def update_pricing(self,adj_factor=0.9):
        '''
        function to adjust product price within a round 

        '''
        self.iter_memory_current['price_consumption_good'] *= adj_factor
            

    def advertise_product(self):
        """
        Currently, we are reaching out to all households available in the market, assuming no frictions
        Some other assumption like, can only apply to x number of household can be implemented as well 
        """
        available_goods = self.not_reserved('consumption_good')
        if available_goods > 0 :
            if self.time[2]>0: ## do not update in the first subround
                self.update_pricing(adj_factor=0.9)
                
            for h in range(self.simulation_parameters['n_households']):                                                 ## advertise to all households 
                self.send(('household',h),'product_ad',{'firm_id':self.id,
                                                        'product':'consumption_good',
                                                        'amount':1,
                                                        'price':self.iter_memory_current['price_consumption_good']})    ## price needs to be determined by some function  
        
    def fill_order(self,verbose=False):
        """
        Try to fill as much order as possible
        """
        msgs = self.get_messages('purchase_order')

        for msg in msgs:
            ## sell goods to households 
            self.sell_goods(household_id = msg['household_id'],n_order = msg['n_orders'])
            
        if verbose:
            logger.info('firm id:{}, orders to be filled: {}'.format(self.id,msgs))
        
        
    def sell_goods(self,household_id=None,n_order=None):
        
        if household_id is None:
            ''' sell goods to ramdom household ''' 
            available_goods = self.not_reserved('consumption_good')
            if available_goods>0:
                self.sell(('household', random.randint(0, self.simulation_parameters['n_households']-1)), 
                          'consumption_good', 
                          quantity=1, 
                          price=self.iter_memory_current['price_consumption_good'])
        else:
            ''' sell goods to specified household ''' 
            available_goods = self.not_reserved('consumption_good')
            if available_goods>0:
                order = self.sell(('household', household_id), 
                                  'consumption_good', 
                                  quantity=min(n_order,available_goods),                                # only offer available amount 
                                  price=self.iter_memory_current['price_consumption_good'])             # 
                        
                self.checkorders.append(order)
    
    def record_order_status(self):
        for o in self.checkorders:
            if o.status == 'accepted':
                res = {'receiver':o.receiver,
                       'quantity':o.final_quantity,
                       'price':o.price}
                self.iter_memory_current['goods_sold'].append(copy.copy(res))
    
    def refresh(self,verbose= False):
        #### reset # labor available  
        #n_labor = self.not_reserved('labor')
        self.destroy('labor')                                                                   ## destroy all available labors 
        self.destroy('consumption_good')                                                        ## destroy all good produced in this round 
        self.checkorders = []
        
        ## reset some memory 
        self.iter_memory_current['labor_hired'] = []
        self.iter_memory_current['goods_sold'] = []
        
        ## print simple summary 
        if verbose:
            logger.info('firm id:{} ; memory: {}'.format(self.id,self.iter_memory_current))
            
        ## empty memory slot for credit
        self.iter_memory_current['new_credit_received'] = 0
        
    

            
    def log_balance(self,verbose=False):
        """
        DES: log all necessary info
        
        """
        self.balance_sheet.update(self.possessions())
        self.iter_memory_current['balance_sheet'] = self.balance_sheet
        self.iter_memory_current['iter'] = self.time[0]
        ## calculate average labor cost 
        labor_df = pd.DataFrame(self.iter_memory_current['labor_hired'])
        if len(labor_df)>0:
            self.iter_memory_current['price_labor'] = abs(labor_df.money.dot(labor_df.labor))/abs(labor_df.labor.sum())
        
        ## calculate consumer good price 
        goods_df = pd.DataFrame(self.iter_memory_current['goods_sold'])
        if len(goods_df)>0:
            self.iter_memory_current['price_consumption_good'] = abs(goods_df.price.dot(goods_df.quantity))/abs(goods_df.quantity.sum())
        
        ## add to history
        self.iter_memory_history.append(copy.copy(self.iter_memory_current))
        
        ## print info 
        if verbose:
            logger.info('firm id:{} ; memory: {}'.format(self.id,self.iter_memory_current))
        
        self.out_iter_memory_current = str(self.iter_memory_current)
        return self.iter_memory_current
        
