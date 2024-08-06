import sys
import os
import random
import subprocess
from tqdm import tqdm
import time

current_dir = os.getcwd()
parent_of_parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir, os.pardir))
sys.path.append(parent_of_parent_dir)

from environment import SumoSimulator
from environment import TrafficEnvironment
from keychain import Keychain as kc
from services import plotter
from services import runner

from create_agents import create_agent_objects
from utilities import check_device
from utilities import get_params
from utilities import set_seeds

from pettingzoo.test import api_test

def main(params):
    env = TrafficEnvironment(params[kc.RUNNER], params[kc.ENVIRONMENT], params[kc.SIMULATOR], params[kc.AGENT_GEN], params[kc.AGENTS], params[kc.PHASE])

    env.start()
    env.reset()

    num_episodes = 100

    for episode in range(num_episodes):
        env.step()


    env.mutation()



    num_episodes = 100

    for episode in range(num_episodes):
        print("episode is: ", episode, "\n\n")
        env.reset()

        while(1):
            observation, reward, termination, truncation, info = env.last()

            if termination or truncation:
                print("truncations break\n\n")
                break
            else:
                # This is where you would insert your policy
                action = random.choice([0, 1])

            env.step(action)

        
    env.stop()

    plotter(params[kc.PLOTTER])


if __name__ == "__main__":
    check_device()
    set_seeds()
    params = get_params(kc.PARAMS_PATH)
    main(params)