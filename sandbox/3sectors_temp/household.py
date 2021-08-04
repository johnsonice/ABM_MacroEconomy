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
        self._inventory._perishable.append('labor')  # TODO simplify this的
        self.checkorder = None
    
    
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
        if self.employer is None:
            #print(self.group, self.id)
            msgs = self.get_messages('conditional_offer')
            employer_id=None ## initiate e_id as none
            if len(msgs)>0:
                employer_id =  random.choice(msgs)['firm_id'] ## decide on one offer
                ## sell labor to firm 
                self.sell_labor(firm_id = employer_id)
                
                
            if print_decision:
                print(self.id)
                print('take offer :{}'.format(employer_id))
            
        
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
            print(self.checkorder,self.employer)
    
    def quite_current_job(self):
        self.employer = None
        
    def buy_goods(self):
        """ make offers to a ramdom firm for comsumption good """
        for offer in self.get_offers("consumption_good"):
            self.accept(offer,min(offer.quantity,
                                   self.not_reserved('money')))
        
    def consumption(self):
        """ consumes_everything and logs the aggregate utility. current_utiliy
        """
        current_utiliy = self.consume(self.utility_function, ['consumption_good'])
        self.accumulated_utility += current_utiliy
        self.log('HH', {'': self.accumulated_utility})
