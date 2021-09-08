import abcEconomics as abce
import random

class Firm(abce.Agent, abce.Firm):
    def init(self,simulation_parameters):
        """ there are now 2 sectors:
        - upstream produces an intermediary good
        - downstream uses labor and the intermediary good to produce the final good

        there is an initial endowment to avoid bootstrapping problems
        """
        self.simulation_parameters = simulation_parameters
        self.create('money', 100)
        self.create('consumption_good', 1)                                                             ## initiate with one good 
        self.inputs = {"labor": 1}
        self.output = "consumption_good"      
        self.cobb_douglas_multiplier = 10
        self.price = {'consumption_good':1,
                      'labor':1}
        # self._inventory._perishable.append('labor') 
        # self._inventory._perishable.append('consumption_good') 
        self.pf = self.create_cobb_douglas(self.output, self.cobb_douglas_multiplier, self.inputs)     ## need to understand this a bit more 
        self.balance_sheet = {}
        self.iter_memory_current ={'iter':0,
                                   'solvency_status': True,
                                   'planned_production': 10,                                            ## very random, default to 4 for now
                                   'labor_needed': 2,
                                   'actual_production':None,
                                   'current_debt':None,
                                   'price_consumption_good':2,
                                   'price_labor':5}
        self.iter_memory_history = []
        
    #################################
    #### Financial Market Open ###### 
    #################################
    def check_financial_viability(self):
        """
        to be implemented; 
        
        check sovency status, if false, delete/refill agent 
        """
        
        return None
        
    
    def plan_production(self,Q=None):
        """
        to be implemented; 
        
        based on historical data, determine current production/ needed inputs / price
        """
        
        
        return None
        
    
    
    def request_credit(self):
        needed_resource = slef.iter_memory_current['labor_needed']*slef.iter_memory_current['price_labor']
        credit_needed = needed_resource - self.not_reserved('money')
        if credit_needed>0:
            ## request for credit 
            self.send(('bank',0),'corporate_debt',{'firm_id':self.id,
                                                   'amount':credit_needed,
                                                    })
        return self.id,credit_needed
        
        
    def filter_applications_and_send_offer(self,n_hires=5,print_apps=False):
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
        #print(self.group, self.id)
        num_hired = self.not_reserved('labor')
        if num_hired < n_hires:  ## check if we hired enough, if not look though offers
            msgs = self.get_messages('application')
            sorted_applications = sorted(msgs, key=lambda k: k['price']) 
            
            if print_apps:
                print('--- firm id:{}; sorted application: {}'.format(self.id,sorted_applications[:n_hires]))
            
            n_openings = n_hires - num_hired        ## get remaining opeining positions 
            for idx,application in enumerate(sorted_applications[:n_hires]):
                if idx < n_openings:                 ## make sure we don exceed max hiring positions 
                    self.send(('household',application['household_id']),'conditional_offer',{'firm_id':self.id})
        else:
            ## else do nothing 
            pass
        
    def buy_inputs(self):
        oo = self.get_offers("labor")
        for offer in oo:
            self.accept(offer,min(offer.quantity,
                                   self.not_reserved('money')))

    def production(self):
        available_inputs = self.not_reserved('labor')
        if available_inputs>0:
            self.produce(self.pf, self.inputs)

    def advertise_product(self):
        """
        Currently, we are reaching out to all households available in the market, assuming no frictions
        Some other assumption like, can only apply to x number of household can be implemented as well 
        """
        for h in range(self.simulation_parameters['n_households']):
            self.send(('household',h),'product_ad',{'firm_id':self.id,
                                                    'product':'consumption_good',
                                                    'amount':1,
                                                    'price':1})    ## price needs to be determined by some function  
        
    def fill_order(self,verbose=False):
        """
        Try to fill as much order as possible
        """
        msgs = self.get_messages('purchase_order')

        for msg in msgs:
            ## sell goods to households 
            self.sell_goods(household_id = msg['household_id'],n_order = msg['n_orders'])
            
        if verbose:
            print('firm id:{}, orders to be filled: {}'.format(self.id,msgs))
        
        
    def sell_goods(self,household_id=None,n_order=None):
        
        if household_id is None:
            ''' sell goods to ramdom household ''' 
            available_goods = self.not_reserved('consumption_good')
            if available_goods>0:
                self.sell(('household', random.randint(0, self.simulation_parameters['n_households']-1)), 
                          'consumption_good', 
                          quantity=1, 
                          price=1)
        else:
            ''' sell goods to specified household ''' 
            available_goods = self.not_reserved('consumption_good')
            if available_goods>0:
                self.sell(('household', household_id), 
                          'consumption_good', 
                          quantity=min(n_order,available_goods),                 # only offer available amount 
                          price=1)                                              # price need to be determined latter 
    
    def refresh(self):
        #### reset # labor available  
        n_labor = self.not_reserved('labor')
        self.destroy('labor')               ## destroy all available labors 
        self.destroy('consumption_good')    ## destroy all good produced in this round 
        pass
    
    
    def log_balance(self,verbose=False):
        """
        DES: log all necessary info
        
        Parameters
        ----------
        verbose : TYPE, optional
            Print out put for debugging. The default is False.
        ----------
        """
        self.balance_sheet = self.possessions()
        if verbose:
            print('firm id:{} ; balalnce: {}'.format(self.id,self.balance_sheet))
        
        return self.balance_sheet
        
    # def sell_goods(self):
    #     """ offers one unit of labor to firm 0, for the price of 1 "money" """
    #     oo = self.get_offers(self.output)
    #     for offer in oo:
    #         self.accept(offer, min(offer.quantity,
    #                                self.possession(self.output)))