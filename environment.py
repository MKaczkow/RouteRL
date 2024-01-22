import pandas as pd
import random
from prettytable import PrettyTable
import numpy as np

from keychain import Keychain as kc
from simulator import Simulator
from agent import Agent

class TrafficEnvironment:

    """
    To be implemented
    """

    def __init__(self, agents): # get params for simulator
        # Initialize network
        # Create demand
        # Create paths
        # Calculate free flows
        # done
        self.simulator = Simulator() # pass params for simulator

        #### 
        # Create 600 agents
        self.print_agents(agents, print_every=50)
        
        
        return None

    def reset(self):
        return None

    def step(self, joint_action):   # For now, returns random rewards
        agent_ids = joint_action[kc.AGENT_ID]

        ####
        #### Feed agents actions to SUMO and get travel times
        ####

        #route_1_rou,route_1_veh,route_2_rou,route_2_veh,time_route1,time_route2,cost1,cost2,df1,df2 = self.simulator.run_simulation_iteration(time_route1, time_route2, route_1_rou, route_2_rou, route_1_veh, route_2_veh, cost1, cost2)


        ###### random - will change
        sumo_df = pd.DataFrame({
            'id': agent_ids,
            'travel_times': np.random.uniform(low=1, high=100, size=len(agent_ids))
        })

        #### Calculate joint reward based on travel times returned by SUMO
        joint_reward = self.calculate_rewards(sumo_df)

        rewards = [joint_reward for i in range(len(agent_ids))]
        joint_reward = pd.DataFrame({kc.AGENT_ID : agent_ids, kc.REWARD : rewards})

        return joint_reward, None, True

    def calculate_rewards(self, sumo_df):
        average_travel_time = sumo_df['travel_times'].mean()

        return average_travel_time

    def print_agents(self, agents, print_every=1): # Should this be even here?
        table = PrettyTable()
        table.field_names = kc.AGENT_ATTRIBUTES

        for a in agents:
            if not (a.id % print_every):
                table.add_row([a.id, a.origin, a.destination, a.start_time, a.__class__.__name__])

        if print_every > 1: print("--- Showing every %dth agent ---" % (print_every))
        print(table)
