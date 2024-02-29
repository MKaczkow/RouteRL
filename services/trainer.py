import concurrent.futures
import pandas as pd
import time

from keychain import Keychain as kc
from services import Plotter
from services import Recorder
from utilities import show_progress_bar


class Trainer:

    """
    Class to train agents
    """

    def __init__(self, params):
        self.num_episodes = params[kc.NUM_EPISODES]
        self.recorder_params = params[kc.RECORDER_PARAMETERS]
        self.plotter_params = params[kc.PLOTTER_PARAMETERS]
        self.remember_every = params[kc.REMEMBER_EVERY]
        self.mutation_time = params[kc.MUTATION_TIME]


    def train(self, env, agents):

        self.recorder = Recorder(self.recorder_params)
        self.plotter = Plotter(self.mutation_time, self.recorder.episodes_folder, self.recorder.agents_folder, self.recorder.sim_length_file_path, self.plotter_params)

        env.start()
        
        print(f"\n[INFO] Training is starting with {self.num_episodes} episodes.")
        
        # Until we simulate num_episode episodes
        start_time = time.time()
        for ep in range(self.num_episodes):

            if ep == self.mutation_time:
                agents = self.mutate_agents(agents)

            observations, infos = env.reset()
            done = False

            # Until the episode concludes
            while not done:

                joint_action = {kc.AGENT_ID : list(), kc.AGENT_KIND : list(), kc.ACTION : list(),
                                kc.AGENT_ORIGIN : list(), kc.AGENT_DESTINATION : list(), kc.AGENT_START_TIME : list()}

                # Every agent picks action
                for agent, observation in zip(agents, observations):
                    action = agent.act(observation)
                    joint_action = self.add_action_to_joint_action(agent, action, joint_action)
                
                joint_action_df = pd.DataFrame(joint_action)
                sample_observation, joint_reward_df, terminated, truncated, info = env.step(joint_action_df)

                self.teach_agents(agents, joint_action_df, joint_reward_df, sample_observation)
                
                done = all(terminated.values())

            self.save(ep, joint_action_df, joint_reward_df, agents, env.get_last_sim_duration())
            show_progress_bar("TRAINING", start_time, ep+1, self.num_episodes)

        self.show_training_time(start_time)
        env.stop()
        self.plotter.visualize_all(self.recorder.episodes)
    


    def teach_agents(self, agents, joint_action_df, joint_reward_df, observation):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.learn_agent, agent, joint_action_df, joint_reward_df, observation) for agent in agents]
            concurrent.futures.wait(futures)
        
    

    def learn_agent(self, agent, joint_action_df, joint_reward_df, observation):
        action = joint_action_df.loc[joint_action_df[kc.AGENT_ID] == agent.id, kc.ACTION].item()
        reward = joint_reward_df.loc[joint_action_df[kc.AGENT_ID] == agent.id, kc.REWARD].item()
        agent.learn(action, reward, observation)
    


    def add_action_to_joint_action(self, agent, action, joint_action):  # Add individual action to joint action
        joint_action[kc.AGENT_ID].append(agent.id)
        joint_action[kc.AGENT_KIND].append(agent.kind)
        joint_action[kc.AGENT_ORIGIN].append(agent.origin)
        joint_action[kc.AGENT_DESTINATION].append(agent.destination)
        joint_action[kc.AGENT_START_TIME].append(agent.start_time)
        joint_action[kc.ACTION].append(action)
        return joint_action
    

    
    def save(self, episode, joint_action_df, joint_reward_df, agents, last_sim_duration):
        if (not (episode % self.remember_every)) or (episode == (self.num_episodes-1)):
            self.recorder.remember_all(episode, joint_action_df, joint_reward_df, agents, last_sim_duration)


    def mutate_agents(self, agents):
        for idx, agent in enumerate(agents):
            if agent.mutate_to is not None:
                new_agent = agent.mutate()
                agents[idx] = new_agent
        return agents

    
    def show_training_time(self, start_time):
        now = time.time()
        training_time = time.strftime("%H hours, %M minutes, %S seconds", time.gmtime(now - start_time))
        print(f"\n[COMPLETE] Training completed in: {training_time}")