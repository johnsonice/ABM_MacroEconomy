import abcEconomics as abce
from random import shuffle, randint

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
        #self.employer = self.id
        self._inventory._perishable.append('labor')  # TODO simplify this

    def sell_labor(self):
        """ offers one unit of labor to a random firm, for the price of 1 "money" """
        self.sell(('firm', randint(0, self.simulation_parameters['n_firms']-1)), 
                  "labor", 
                  quantity=1, 
                  price=1)

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
