from environment import TrafficEnvironment
from keychain import Keychain as kc
from services import Trainer
from services import create_agent_objects
from services import confirm_env_variable
from services import get_json

confirm_env_variable(kc.SUMO_HOME, append="tools")
params = get_json(kc.PARAMS_PATH)

"""
Next Improvement:
1. First, determine number of agents first (read from params.json), give it to simulator, get freeflow times, use this info in agent generation
2. Pass this to simulator
3. Calculate the freeflow travel times
4. Only then generate agents, by also using freeflow information for initial knowledge for human agents
"""

def main():

    agents = create_agent_objects(params[kc.AGENTS_GENERATION_PARAMETERS])
    env = TrafficEnvironment(agents) # pass some params for the simulation

    free_flow_cost = env.calculate_free_flow_time()
    print(free_flow_cost)
    
    trainer = Trainer(params[kc.TRAINING_PARAMETERS])
    agents = trainer.train(env, agents)


main()