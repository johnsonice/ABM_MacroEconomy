import abcEconomics as abce
import random
#from random import shuffle, randint

class Household(abce.Agent, abce.Household):
    def init(self,simulation_parameters):
        """ self.employer is the _number_ of the agent that receives his
        labor offer.
        """
        self.simulation_parameters = simulation_parameters
        self.labor_endowment = 1
        self.create('money', 100)
        self.utility_function = self.create_cobb_douglas_utility_function({"consumption_good": 1})
        self.accumulated_utility = 0
        self.employer = None
        self._inventory._perishable.append('labor')  # TODO simplify this
        self.checkorder = None
        self.balance_sheet = {}
    
    
    #################################
    #### Labor Market operations 
    #################################
    def apply_for_jobs(self):
        """
        Currently, we are applying to all firms available in the market, assuming no frictions
        Some other assumption like, can only apply to x number of frims can be implemented as well 

        """
        if self.employer is None:
            for f in range(self.simulation_parameters['n_firms']):
                self.send(('firm',f),'application',{'household_id':self.id,
                                                      'product':'labor',
                                                      'amount':1,
                                                      'price':1})
                
    def take_offer(self,print_decision=False):
        """
        pick one conditional offer and sell labor 
        """
        if self.employer is None:
            #print(self.group, self.id)
            msgs = self.get_messages('conditional_offer')
            employer_id=None ## initiate e_id as none
            if len(msgs)>0:
                employer_id =  random.choice(msgs)['firm_id'] ## decide on one offer
                ## sell labor to firm 
                self.sell_labor(firm_id = employer_id)
                
                
            if print_decision:
                print('household id: {}, take offer :{}'.format(self.id,employer_id))
            
        
    def sell_labor(self,firm_id=None):
        if firm_id is None:
            """ offers one unit of labor to a random firm, for the price of 1 "money" """
            self.sell(('firm', random.randint(0, self.simulation_parameters['n_firms']-1)), 
                      "labor", 
                      quantity=1, 
                      price=1)
        else:
            """ offers one unit of labor to a specific firm, for the price of 1 "money" """
            offer = self.sell(('firm', firm_id), 
                              "labor", 
                              quantity=1, 
                              price=1)
            self.checkorder = offer
    
    def check_job_offer(self,verbose=False):
        if self.checkorder is not None:
            if self.checkorder.status == 'accepted':
                #pass
                self.employer = self.checkorder.receiver[1]
            
        if verbose:
            if self.checkorder is not None:
                print(vars(self.checkorder),self.employer)
            else:
                print(self.checkorder,self.employer)
        
    #################################
    #### Good Market operations 
    #################################
        
    def filter_ads(self,n_consume=2,verbose=False):
        """
        filter all ads and purchase from the lower price 
        """
        
        num_purchased = self.not_reserved('consumption_good')
        msgs = self.get_messages('product_ad')
        sorted_msgs = sorted(msgs, key=lambda k: k['price']) 


        n_buy = n_consume - num_purchased                                                       ## get remaining opeining positions 
        picked_ad =  random.choice(sorted_msgs[:5])                                             ## choice between top 5
        
        if verbose:
            print('--- household id:{}; picked product offer: {}'.format(self.id,picked_ad))
            
        ###### we need to check available money at some point    #####                                                          
        self.send(('firm',picked_ad['firm_id']),
                  'purchase_order',
                  {'household_id':self.id,'n_orders':n_buy})
        
        
        
    def buy_goods(self, verbose=False):
        """ make offers to a ramdom firm for comsumption good """
        offers = self.get_offers("consumption_good")
        for offer in offers:
            self.accept(offer,min(offer.quantity,
                                   self.not_reserved('money')))
        
        if verbose:
            print("household id: {}, take comsumer gppd offer:{}".format(self.id,offers))
        
    def consumption(self):
        """ 
            consumes_everything and logs the aggregate utility. current_utiliy
        """
        current_utiliy = self.consume(self.utility_function, ['consumption_good'])
        self.accumulated_utility += current_utiliy
        self.log('HH', {'': self.accumulated_utility})


    def refresh(self):
        #### reset employer 
        self.employer = None
        self.checkorder = None

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
        self.balance_sheet['employer'] = self.employer
        if verbose:
            print('household id:{} ; balalnce: {}'.format(self.id,self.balance_sheet))

    