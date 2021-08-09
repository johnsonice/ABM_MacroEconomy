""" 

Most basic 2 sector model, Firms hire random households for labor, produce consumption good and sell to ramdom households, 
House earn wage from selling their laobr, buys comsumer goods and accumulate utility

"""
import abcEconomics as abce
from abcEconomics import Simulation
# from firm import Firm
# from household import Household


from random import randrange

class Kid(abce.Agent):
    def init(self, num_dealers):
        self.num_dealers = num_dealers
        self.create('money', 100)  # don't we all wish you'd this function in real live?
    
    def print_offers(self):
        print(self.group, self.id)
        msgs = self.get_messages('quote')
        for m in msgs:
            print(m)
        #print(self.get_messages('quote'))
        
        
    def buy_drugs(self):
        drug_dealer_id = randrange(self.num_dealers)
        self.buy(('drug_dealer', drug_dealer_id), good='drugs', quantity=1, price=10)
    
    def print_possessions(self):
        print('    ' + self.group + str(dict(self.possessions())))
        

class DrugDealer(abce.Agent):
    def init(self):
        self.create('drugs', 1)
        
    def advertise(self):
        for k in range(5):
            self.send(('customer',k),'quote',{'product':'drugs',
                                             'price':self.id})
        
    def sell_to_customers(self):
        for offer in self.get_offers('drugs'):
            if offer.price >= 10 and self['drugs'] >= 1:
                self.accept(offer)
    
    def print_possessions(self):
        print('    ' + self.group + str(dict(self.possessions())))
        
        
#%%
if __name__ == '__main__':
    num_dealers = 2
    simulation = abce.Simulation(name='school_yard', processes=1)
    drug_dealers = simulation.build_agents(DrugDealer, 'drug_dealer', number=num_dealers)
    
    customers = simulation.build_agents(Kid, 'customer', number=5, 
                                       num_dealers=num_dealers)
    
    kids = drug_dealers + customers
    
    for r in range(4):
        simulation.advance_round((r))
        print(simulation.time)
        for i in range(4):
            simulation.advance_round((r,i))
            print('iteration {}:{}'.format(r,i))
            print(simulation.time)
            if i > 2:
                pass
            else:
                drug_dealers.advertise()
                
            customers.print_offers()
            kids.print_possessions()
            print()
