""" 

Most basic 2 sector model, Firms hire random households for labor, produce consumption good and sell to ramdom households, 
House earn wage from selling their laobr, buys comsumer goods and accumulate utility

"""
from abcEconomics import Simulation
from firm import Firm
from household import Household
from bank import Bank
import config
from utils import setup_custom_logger,clean_and_refill_firms
import random
import numpy as np
random.seed(config.simulation_parameters['random_seed'])
np.random.seed(config.simulation_parameters['random_seed'])
from utils import print_random

logger = setup_custom_logger('main')

#%%
w = Simulation(processes=1,random_seed = config.simulation_parameters['random_seed']) ## set to 1 for debugging purpose 

firms = w.build_agents(Firm, 'firm', config.simulation_parameters['n_firms'], simulation_parameters = config.simulation_parameters)
households = w.build_agents(Household, 'household', config.simulation_parameters['n_households'],simulation_parameters = config.simulation_parameters)
banks = w.build_agents(Bank, 'bank', config.simulation_parameters['n_banks'],simulation_parameters = config.simulation_parameters)

#%%
for r in range(config.simulation_parameters['rounds']):
    w.advance_round(r)
    logger.info('itetration:{}'.format(w.time))
    
    ###########################
    ## Publish Policy Rate ####
    ###########################
    banks.update_policy_rate()
    policy_rate_info = banks.return_public_info()
    
    ###########################
    #### Financial Market open#
    ###########################
    firms.receive_policy_rate_info(info=policy_rate_info)
    d_firms = firms.check_financial_viability(verbose=False)
    banks.collect_payment()
    ## delete default firms                                                         ## also need to refill firms if needed 
    clean_and_refill_firms(d_firms,firms,logger)
    households.receive_available_firms(firms.names)
    
    ## plan production and get loans 
    firms.plan_production(verbose=False)
    firms.request_credit(verbose=False)
    
    banks.distribute_credit(verbose=False)
    firms.record_debt()
    banks.log_balance_sheet(verbose=False)
    
    ###########################
    #### Labor Market Open ####
    ###########################
    households.refresh_services('labor', derived_from='labor_endowment', units=1)
            # firms.log_balance(verbose=True)                                       ## put all info in balance sheet
            # households.log_balance(verbose=True)                                  ## put all info in balance sheet
    for sub_r_l in range(config.simulation_parameters['sub_hiring_rounds']):
        w.advance_round((r,sub_r_l))                                                ## there could be multiple rounds of applications
        logger.info('itetration: {}'.format(w.time))
        households.apply_for_jobs()                                                 ## send messages to all firms
        firms.filter_applications_and_send_offer(verbose=False)                     ## filter and message to top 5 candidates
        households.take_offer(verbose=False)                                        ## hoursehold take the best offer and send back to firm
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
    for sub_r_g in range(config.simulation_parameters['sub_purchase_rounds']):
        w.advance_round((r,sub_r_l,sub_r_g))
        logger.info('itetration: {}'.format(w.time))
        firms.advertise_product()
        households.filter_ads(min_consume=1)
        firms.fill_order()
        households.buy_goods()
    
    
    firms.record_order_status()                                                     ## record goolds sold for global pricing calculation
    households.consumption()
    
    ###########################
    #### Clean up things ######
    ###########################
    fb = firms.log_balance(verbose=True)                                           ## put all info in balance sheet
    hb = households.log_balance(verbose=False)                                      ## put all info in balance sheet

    #### log status ###
    firms.panel_log(goods=['production','consumption_good'],
                    variables=['out_iter_memory_current'])
    households.panel_log(variables=['accumulated_utility',
                                    'labor_price',
                                    'out_balance_sheet'])
    banks.panel_log(goods=['money'],
                    variables=['policy_rate',
                               'out_financial_account'])
    
    ## clear memory for next round 
    (households + firms).refresh(verbose= False)                                     ## firms labor = 0 ; household.employer = none
                                                                                    ## clear all memories 
w.finalize()


# if __name__ == '__main__':
#     main(simulation_parameters)
