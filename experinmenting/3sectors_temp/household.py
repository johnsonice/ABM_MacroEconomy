import abcEconomics as abce
import random, math
from utils import setup_custom_logger
from abcEconomics import NotEnoughGoods

logger = setup_custom_logger(__name__)
#from random import shuffle, randint

class Household(abce.Agent, abce.Household):
    def init(self,simulation_parameters):
        """ self.employer is the _number_ of the agent that receives his
        labor offer.
        """
        self.simulation_parameters = simulation_parameters
        self.labor_endowment = 1
        self.create('money', 100)
        self.cash_buffer = 100
        self.utility_function = self.create_cobb_douglas_utility_function({"consumption_good": 1})
        self.accumulated_utility = 0
        self.employer = None
        self.available_firms = None
        self._inventory._perishable.append('labor')                         ## TODO simplify this
        self.checkorder = None
        self.labor_price = 4 + random.normalvariate(1,0.2)                  ## some random distribution of wages requirments
        self.consumption_good_price = self.labor_price
        self.balance_sheet = {}
        self.out_balance_sheet = str(self.balance_sheet)
    
    
    #################################
    #### Labor Market operations 
    #################################
    
    def receive_available_firms(self,fs):
        self.available_firms = fs
        
    def update_labor_asking_price(self,verbose=False):
        ### ok, here we need to check see if labor is previous hired , if so increase asking price for next round
        employed = self.balance_sheet.get('employer')
        if employed:
            price_multiplier = 1.05
            #print(employed,price_multiplier)
        else:
            price_multiplier = 1
        
        self.labor_price *= price_multiplier                    ## asking for x % salary increast
        if self.labor_price < self.consumption_good_price:
            self.labor_price = self.consumption_good_price
        if verbose:
            logger.info('household id: {}, asking salary:{}'.format(self.id,self.labor_price))
                                                                    
    def apply_for_jobs(self):
        """
        Currently, we are applying to all firms available in the market, assuming no frictions
        Some other assumption like, can only apply to x number of frims can be implemented as well 

        """
        if self.employer is None:
            if self.time[1] == 0:                                                                   ## first time apply
                self.update_labor_asking_price(False)                                               ## calculating asking price when first apply
                for f in self.available_firms:                                                      ## send applications to all firms 
                    self.send(f,'application',{'household_id':self.id,
                                                          'product':'labor',
                                                          'amount':1,
                                                          'price':self.labor_price})
            else:                                                                                   ## second time apply, lower price
                self.labor_price = max(self.labor_price-random.normalvariate(0,0.2),0.0001)                     ## lower asking price
                for f in self.available_firms:                                                      ## send applications to all firms 
                    self.send(f,'application',{'household_id':self.id,
                                                          'product':'labor',
                                                          'amount':1,
                                                          'price':self.labor_price})
                    
    def take_offer(self,verbose=False):
        """
        pick one conditional offer and sell labor 
        """
        if self.employer is None:
            #logger.info(self.group, self.id)
            msgs = self.get_messages('conditional_offer')
            employer_id=None ## initiate e_id as none
            
            if len(msgs)>0:
                sorted_offers = sorted(msgs, key=lambda k: k['salary'],reverse=True)        ## take the highest offer
                
                employer_id =  random.choice(sorted_offers[:5])['firm_id']                  ## decide on one offer
                #employer_id =  sorted_offers[0]['firm_id']                                 ## decide on the highest offer
                salary = sorted_offers[0]['salary'] 
                ## sell labor to firm 
                self.sell_labor(firm_id = employer_id,salary=salary)
                
                if verbose:
                    logger.info('household id: {}, take offer :{}, at price: {}; all_offers:{}'.format(self.id,
                                                                                                       employer_id,
                                                                                                       salary,
                                                                                                       sorted_offers))
            
        return self.balance_sheet
    
    def sell_labor(self,firm_id=None,salary=None):
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
                              price=salary)
            self.checkorder = offer
    
    def check_job_offer(self,verbose=False):
        if self.checkorder is not None:
            if self.checkorder.status == 'accepted':
                #pass
                self.employer = self.checkorder.receiver[1]
                self.labor_price = self.checkorder.price
            
        if verbose:
            if self.checkorder is not None:
                logger.info(vars(self.checkorder),self.employer)
            else:
                logger.info(self.checkorder,self.employer)
        
    #################################
    #### Good Market operations 
    #################################
        
    def filter_ads(self,min_consume=1,verbose=False):
        """
        filter all ads and purchase from the lower price 
        """
        
        num_purchased = self.not_reserved('consumption_good')                                       ## # of goods already purchased from previous round
        msgs = self.get_messages('product_ad')
        sorted_msgs = sorted(msgs, key=lambda k: k['price']) 

        ## calculate demand 

        disposable_money = self.not_reserved('money') - self.cash_buffer                            ## sepend everything
        
        ## calculate # of goods to buy ##
        
        if len(sorted_msgs) > 0:
            #picked_ad = sorted_msgs[0]                                                             ## pick the lowest one
            picked_ad =  random.choice(sorted_msgs[:5])                                             ## choice between top 5
            n_buy =  max(0,math.floor(disposable_money/picked_ad['price']))                         ## can not go negative
            
            if num_purchased == 0 and n_buy <= 0:
                n_buy = min_consume                                                                 ## minimum purchase is 1 
            
            if verbose:
                logger.info('--- household id:{}; picked product offer: {}, # of purchases:{}'.format(self.id,picked_ad,n_buy))
                                                                       
            self.send(('firm',picked_ad['firm_id']),
                      'purchase_order',
                      {'household_id':self.id,'n_orders':n_buy})
            
        
    def buy_goods(self, verbose=False):
        """ make offers to a ramdom firm for comsumption good """
        offers = self.get_offers("consumption_good")
        for offer in offers:
            try:
                self.accept(offer,offer.quantity)                                                   ## quantity is calculated in messaging section
            except NotEnoughGoods:
                self.reject(offer)
            
            self.consumption_good_price = offer.price
            
        if verbose:
            logger.info("household id: {}, take comsumer gppd offer:{}".format(self.id,offers))
        
    def consumption(self):
        """ 
            consumes_everything and logs the aggregate utility. current_utiliy
        """
        current_utiliy = self.consume(self.utility_function, ['consumption_good'])
        self.accumulated_utility += current_utiliy
        self.log('HH', {'': self.accumulated_utility})
    
    #################################
    #### Clean up memory 
    #################################

    def refresh(self,verbose=False):
        #### reset employer 
        self.employer = None
        self.checkorder = None

    def log_balance(self,verbose=False):
        """
        DES: log all necessary info
        
        Parameters
        ----------
        verbose : TYPE, optional
            logger.info out put for debugging. The default is False.
        ----------
        """
        self.balance_sheet = self.possessions()
        self.balance_sheet['employer'] = self.employer
        self.out_balance_sheet= str(self.balance_sheet)
        if verbose:
            logger.info('household id:{} ; balalnce: {}'.format(self.id,self.balance_sheet))

        return self.balance_sheet