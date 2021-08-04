import abcEconomics as abce
from random import shuffle, randint

class Firm(abce.Agent, abce.Firm):
    def init(self,simulation_parameters):
        """ there are now 2 sectors:
        - upstream produces an intermediary good
        - downstream uses labor and the intermediary good to produce the final good

        there is an initial endowment to avoid bootstrapping problems
        """
        self.simulation_parameters = simulation_parameters
        self.price = {}
        self.create('money', 100)
        self.create('consumption_good', 1)    # initiate with one good 
        self.inputs = {"labor": 1}
        self.output = "consumption_good"      
        self.outquatity = 2
        self.price['consumption_good'] = 1
        self.pf = self.create_cobb_douglas(self.output, self.outquatity, self.inputs)

    
    def filter_applications_and_send_offer(self,n_hires=5,print_apps=False):
        """
        Parameters
        ----------
        n_hires : int, optional
            DESCRIPTION. The default is 5.
            number of employees firm would like to hire in this iteration 
        Returns
        -------
        send out conditional offer to qualified candidates
        None.
        """
        #print(self.group, self.id)
        msgs = self.get_messages('application')
        sorted_applications = sorted(msgs, key=lambda k: k['price']) 
        
        if print_apps:
            print(self.id)
            print(sorted_applications[:n_hires])
            
        for application in sorted_applications[:n_hires]:
            self.send(('household',application['household_id']),'conditional_offer',{'firm_id':self.id})

        
    def buy_inputs(self):
        oo = self.get_offers("labor")
        for offer in oo:
            self.accept(offer,min(offer.quantity,
                                   self.not_reserved('money')))

    def production(self):
        available_inputs = self.not_reserved('labor')
        if available_inputs>0:
            self.produce(self.pf, self.inputs)

    def sell_goods(self):
        ''' sell goods to ramdom household ''' 
        available_goods = self.not_reserved('consumption_good')
        if available_goods>0:
            self.sell(('household', randint(0, self.simulation_parameters['n_households']-1)), 
                      'consumption_good', 
                      quantity=1, 
                      price=1)
    
    # def sell_goods(self):
    #     """ offers one unit of labor to firm 0, for the price of 1 "money" """
    #     oo = self.get_offers(self.output)
    #     for offer in oo:
    #         self.accept(offer, min(offer.quantity,
    #                                self.possession(self.output)))