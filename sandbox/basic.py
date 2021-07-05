import abcEconomics as abce


class Agent(abce.Agent):
    def init(self, world_size, family_name):
        self.family_name = family_name
        self.world_size = world_size
        print(world_size)
        
    def say(self):
        print("hello I am %s my id %i and my group is '%s', it is the %i round" % (self.family_name, self.id, self.group, self.time))
#%%
def main():

    simulation = abce.Simulation(name='abce', processes=1)
    
    agents = simulation.build_agents(Agent, 'agent',
                                     world_size=30,
                                     agent_parameters=[{'family_name': 'fred'}, 
                                                       {'family_name': 'astaire'}, 
                                                       {'family_name': 'altair'}, 
                                                       {'family_name': 'deurich'}])

    for r in range(5):
        simulation.time = r
        agents.say()
        
    simulation.finalize()

if __name__ == "__main__":
    main()