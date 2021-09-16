""" 

Most basic 2 sector model, Firms hire random households for labor, produce consumption good and sell to ramdom households, 
House earn wage from selling their laobr, buys comsumer goods and accumulate utility

"""
from abcEconomics import Simulation
from firm import Firm
from household import Household
from bank import Bank


simulation_parameters = {'random_seed': 1,
                         'n_firms':4,
                         'n_households':20,
                         'n_banks':1,
                         'rounds':10,
                         'sub_hiring_rounds':4,
                         'sub_purchase_rounds':1}

w = Simulation(processes=1) ## set to 1 for debugging purpose 

firms = w.build_agents(Firm, 'firm', simulation_parameters['n_firms'], simulation_parameters = simulation_parameters)
households = w.build_agents(Household, 'household', simulation_parameters['n_households'],simulation_parameters = simulation_parameters)
banks = w.build_agents(Bank, 'bank', simulation_parameters['n_banks'],simulation_parameters = simulation_parameters)

#%%
for r in range(simulation_parameters['rounds']):
    w.advance_round(r)
    print('itetration:{}'.format(w.time))
    
    ###########################
    ## Publish Policy Rate 
    ###########################
    
    banks.update_policy_rate()
    policy_rate_info = banks.return_public_info()
    
    ###########################
    #### Financial Market open#
    ###########################
    
    firms.receive_policy_rate_info(info=policy_rate_info)
    
    d_firms = firms.check_financial_viability(verbose=True)
    banks.collect_payment()
    
    ## delete default firms                                                         ## also need to refill firms if needed 
    dfs = [i for i in d_firms[0] if i is not None]
    if len(dfs)>0:
        firms.delete_agents(dfs)
        print("Delete frims: {}".format(dfs))
    else:
        print('no frims dropped out this round')
    
    households.receive_available_firms(firms.names)
    
    ## plan production and get loans 
    firms.plan_production(verbose=True)
    firms.request_credit(verbose=True)
    
    banks.distribute_credit(verbose=True)
    firms.record_debt()
    banks.log_balance_sheet(verbose=True)
    
    ###########################
    #### Labor Market Open ####
    ###########################
    
    households.refresh_services('labor', derived_from='labor_endowment', units=1)
            ## for debug, print initial possessions 
            # firms.log_balance(verbose=True)                                       ## put all info in balance sheet
            # households.log_balance(verbose=True)                                  ## put all info in balance sheet
    for sub_r_l in range(simulation_parameters['sub_hiring_rounds']):
        w.advance_round((r,sub_r_l))                                                  ## there could be multiple rounds of applications
        print('itetration: {}'.format(w.time))
        households.apply_for_jobs()                                                 ## send messages to all firms
        firms.filter_applications_and_send_offer(print_apps=False)                  ## filter and message to top 5 candidates
        households.take_offer(print_decision=False)                                 ## hoursehold take the best offer and send back to firm
                                                                                    ## households.sell_labor() already part of take_offer
        firms.buy_inputs(verbose=False)                                             ## firm hire labor from the confirmed offer sent back from candidates
        households.check_job_offer(verbose=False)                                   ## see if is hired and update employer id
        
    ###########################
    #### Production Begain ####
    ###########################
    
    firms.production()                                                              ## use all available labor to product consumer product
    
    ###########################
    #### Goods Market Open ####
    ###########################
    
    ######## should we add multiple rounds here, maybe yes  ??????????????????????
    for sub_r_g in range(simulation_parameters['sub_purchase_rounds']):
        w.advance_round((r,sub_r_l,sub_r_g))
        print('itetration: {}'.format(w.time))
        firms.advertise_product()
        households.filter_ads(min_consume=1)
        firms.fill_order()
        households.buy_goods()
        households.consumption()
    
    ###########################
    #### Clean up things ######
    ###########################
    
    fb = firms.log_balance(verbose=True)                                            ## put all info in balance sheet
    hb = households.log_balance(verbose=False)                                      ## put all info in balance sheet
    (households + firms).refresh()                                                  ## firms labor = 0 ; household.employer = none
                                                                                    ## check order = None
                                                                                    
                                                                                  
    # firms.panel_log(goods=['consumption_good'])
    # households.panel_log(goods=['consumption_good'])

w.finalize()


# if __name__ == '__main__':
    #main(simulation_parameters)
