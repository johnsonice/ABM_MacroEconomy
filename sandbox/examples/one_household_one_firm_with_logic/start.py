""" 1. declared the timeline
    2. build one Household and one Firm follow_agent
    3. For every labor_endowment an agent has he gets one trade or usable labor
    per round. If it is not used at the end of the round it disapears.
    4. Firms' and Households' possesions are monitored ot the points marked in
    timeline.
"""

from abcEconomics import Simulation
from firm import Firm
from household import Household

parameters = {'name': '2x2',
              'random_seed': None,
              'rounds': 2500,
              'num_firms': 10}

def main(parameters):
    simulation = Simulation(processes=1)

    firms = simulation.build_agents(
        Firm, 'firm', number=parameters['num_firms'])
    households = simulation.build_agents(
        Household, 'household', number=1,num_firms=parameters['num_firms'])#, parameters=parameters)

    try:
        for rnd in range(parameters['rounds']):
            simulation.advance_round(rnd)
            households.refresh_services('labor', derived_from='adult', units=1)
            households.sell_labor()
            firms.buy_labor()
            firms.production()
            firms.panel_log(possessions=['money', 'GOOD'],
                            variables=['price', 'inventory'])
            firms.quotes()
            households.buy_goods()
            firms.sell_goods()
            households.agg_log(possessions=['money', 'GOOD'],
                               variables=['current_utiliy'])
            households.consumption()
            firms.adjust_price()
    except Exception as e:
        print(e)
    simulation.finalize()


if __name__ == '__main__':
    main(parameters)
