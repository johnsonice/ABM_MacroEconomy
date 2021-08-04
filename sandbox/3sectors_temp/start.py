""" 

Most basic 2 sector model, Firms hire random households for labor, produce consumption good and sell to ramdom households, 
House earn wage from selling their laobr, buys comsumer goods and accumulate utility

"""
from abcEconomics import Simulation
from firm import Firm
from household import Household


simulation_parameters = {'random_seed': 1,
                         'n_firms':10,
                         'n_households':10,
                         'rounds':10}

def main(simulation_parameters):
    w = Simulation()

    firms = w.build_agents(Firm, 'firm', simulation_parameters['n_firms'], simulation_parameters = simulation_parameters)
    households = w.build_agents(Household, 'household', simulation_parameters['n_households'],simulation_parameters = simulation_parameters)

    for r in range(simulation_parameters['rounds']):
        print('itetration:{}'.format(r))
        w.advance_round(r)
        households.refresh_services('labor', derived_from='labor_endowment', units=2)
        households.apply_for_jobs()
        firms.filter_applications_and_send_offer(n_hires=5,print_apps=False)
        households.take_offer(print_decision=True)
        firms.buy_inputs()
        households.check_job_offer(True)  ## update employer id
        # households.sell_labor()
        # firms.buy_inputs()
        # firms.production()
        # firms.panel_log(goods=['consumption_good'])
        # firms.sell_goods()
        # households.buy_goods()
        # households.panel_log(goods=['consumption_good'])
        # households.consumption()
        
    w.finalize()


if __name__ == '__main__':
    main(simulation_parameters)
