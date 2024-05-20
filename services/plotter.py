import matplotlib.pyplot as plt
import os
import pandas as pd
import seaborn as sns

from collections import Counter
from statistics import mean
from statistics import variance

from keychain import Keychain as kc
from utilities import make_dir
from utilities import running_average



class Plotter:


    """
    This class is to plot the results of the training
    """


    def __init__(self, mutation_time, second_mutation_time, from_recorder, params):

        self.episodes_folder = from_recorder.episodes_folder
        self.agents_folder = from_recorder.agents_folder
        self.sim_length_file_path = from_recorder.sim_length_file_path
        self.loss_file_path = from_recorder.loss_file_path
        self.free_flow_times_file_path = os.path.join(kc.RECORDS_FOLDER, kc.FREE_FLOW_TIMES_CSV_FILE_NAME)

        self.saved_episodes = list()
        self.mutation_time = mutation_time
        self.second_mutation_time = second_mutation_time
        self.machine_episodes = list()
        self.machine2_episodes = list()

        self.default_width, self.default_height = 12, 6
        self.multimode_width, self.multimode_height = 8, 5
        self.default_num_columns = 2

        print(f"[SUCCESS] Plotter is now here to plot!")


#################### VISUALIZE ALL

    def visualize_all(self, episodes):
        self.saved_episodes = episodes
        self.machine_episodes = [ep for ep in self.saved_episodes if ep >= self.mutation_time]
        self.machine2_episodes = [ep for ep in self.saved_episodes if ep >= self.second_mutation_time]

        self.visualize_free_flows()
        self.visualize_mean_rewards()
        self.visualize_mean_travel_times()
        self.visualize_tt_distributions()
        self.visualize_flows()
        self.visualize_actions()
        self.visualize_action_shifts()
        self.visualize_sim_length()
        self.visualize_losses()

####################


#################### FREE FLOWS
        
    def visualize_free_flows(self):
        save_to = make_dir(kc.PLOTS_FOLDER, kc.FF_TRAVEL_TIME_PLOT_FILE_NAME)

        free_flows = self.retrieve_free_flows()
        od_pairs = list(set(free_flows[['origins', 'destinations']].apply(lambda x: (x.iloc[0], x.iloc[1]), axis=1)))
        num_od_pairs = len(od_pairs)
        
        num_columns = self.default_num_columns
        num_rows = (num_od_pairs + num_columns - 1) // num_columns

        figure_size = (self.multimode_width * num_columns, self.multimode_height * num_rows)
        fig, axes = plt.subplots(num_rows, num_columns, figsize=figure_size)
        fig.tight_layout(pad=5.0)

        if num_rows > 1:   axes = axes.flatten()   # Flatten axes

        od_pairs.sort()
        for idx, od in enumerate(od_pairs):
            ax = axes[idx]
            subset = free_flows[free_flows[kc.ORIGINS] == od[0]]
            subset = subset[subset[kc.DESTINATIONS] == od[1]]
            for _, row in subset.iterrows():
                ax.bar(f"{row[kc.PATH_INDEX]}", row[kc.FREE_FLOW_TIME], label = f"Route: {int(row[kc.PATH_INDEX])}")

            ax.set_title(f"Free flow travel times in {od[0]}-{od[1]}")
            ax.set_xlabel('Route Index')
            ax.set_ylabel('Minutes')
            ax.legend()

        for ax in axes[idx+1:]:   ax.axis('off')    # Hide unused subplots if any

        #plt.show()
        plt.savefig(save_to)
        plt.close()
        print(f"[SUCCESS] Free-flow travel times are saved to {save_to}")



    def retrieve_free_flows(self):
        free_flows = pd.read_csv(self.free_flow_times_file_path)
        free_flows = free_flows.astype({kc.ORIGINS: 'int', kc.DESTINATIONS: 'int', kc.PATH_INDEX: 'int', kc.FREE_FLOW_TIME: 'float'})
        return free_flows
        
####################    


#################### REWARDS
    
    def visualize_mean_rewards(self):
        save_to = make_dir(kc.PLOTS_FOLDER, kc.REWARDS_PLOT_FILE_NAME)
        all_rewards = self.retrieve_reward_per_kind()
        all_mean_rewards, mean_human_rewards, mean_machine_rewards, mean_machine2_rewards = self.retrieve_mean_rewards(all_rewards)

        plt.figure(figsize=(self.default_width, self.default_height))

        plt.plot(self.saved_episodes, running_average(mean_human_rewards, last_n=3), label="Humans")
        plt.plot(self.machine_episodes, running_average(mean_machine_rewards, last_n=3), label="Machines")
        plt.plot(self.machine2_episodes, running_average(mean_machine2_rewards, last_n=3), label="Disruptive")
        #plt.plot(self.saved_episodes, running_average(all_mean_rewards, last_n=3), label="All")   # Before machines, it is just humans

        plt.axvline(x = self.mutation_time, label = 'Mutation Time', color = 'r', linestyle = '--')
        plt.axvline(x = self.second_mutation_time, label = 'Mutation Time 2', color = 'b', linestyle = '--')
        plt.xlabel('Episode')
        plt.ylabel('Mean Reward')
        plt.title('Mean Rewards Over Episodes (n = 3)')
        plt.legend()

        plt.savefig(save_to)
        plt.close()
        print(f"[SUCCESS] Rewards are saved to {save_to}")
        

    def retrieve_reward_per_kind(self):
        all_rewards = {kc.TYPE_HUMAN: list(), kc.TYPE_MACHINE: list(), kc.TYPE_MACHINE_2: list()}
        for episode in self.saved_episodes:
            data_path = os.path.join(self.episodes_folder, f"ep{episode}.csv")
            data = pd.read_csv(data_path)
            kinds, rewards = data[kc.AGENT_KIND], data[kc.REWARD]
            rewards_per_kind =  {kc.TYPE_HUMAN: list(), kc.TYPE_MACHINE: list(), kc.TYPE_MACHINE_2: list()}
            for kind, reward in zip(kinds, rewards):
                rewards_per_kind[kind].append(reward)
            for kind in rewards_per_kind.keys():
                all_rewards[kind].append(rewards_per_kind[kind])
        return all_rewards


    
    def retrieve_mean_rewards(self, all_rewards):
        all_mean_rewards, mean_human_rewards, mean_machine_rewards, mean_machine2_rewards = list(), list(), list(), list()

        for idx, ep in enumerate(self.saved_episodes):
            human_rewards = all_rewards[kc.TYPE_HUMAN][idx]
            rewards = human_rewards
            mean_human_rewards.append(mean(human_rewards))
            
            if ep >= self.mutation_time:
                machine_rewards = all_rewards[kc.TYPE_MACHINE][idx]
                rewards = rewards + machine_rewards
                mean_machine_rewards.append(mean(machine_rewards))

            if ep >= self.second_mutation_time:
                machine2_rewards = all_rewards[kc.TYPE_MACHINE_2][idx]
                rewards = rewards + machine2_rewards
                mean_machine2_rewards.append(mean(machine2_rewards))
            
            all_mean_rewards.append(mean(rewards))

        return all_mean_rewards, mean_human_rewards, mean_machine_rewards, mean_machine2_rewards

####################   


#################### TRAVEL TIMES
    
    def visualize_mean_travel_times(self):
        save_to = make_dir(kc.PLOTS_FOLDER, kc.TRAVEL_TIMES_PLOT_FILE_NAME)
        all_travel_times = self.retrieve_tt_per_kind()
        all_mean_tt, mean_human_tt, mean_machine_tt, mean_machine2_tt = self.retrieve_mean_tt(all_travel_times)

        plt.figure(figsize=(self.default_width, self.default_height))

        plt.plot(self.saved_episodes, running_average(all_mean_tt, last_n=3), label="All")   # Before machines, it is just humans
        plt.plot(self.saved_episodes, running_average(mean_human_tt, last_n=3), label="Humans")
        plt.plot(self.machine_episodes, running_average(mean_machine_tt, last_n=3), label="Machines")
        plt.plot(self.machine2_episodes, running_average(mean_machine2_tt, last_n=3), label="Disruptive")

        plt.axvline(x = self.mutation_time, label = 'Mutation Time', color = 'r', linestyle = '--')
        plt.axvline(x = self.second_mutation_time, label = 'Mutation Time 2', color = 'b', linestyle = '--')
        plt.xlabel('Episode')
        plt.ylabel('Mean Travel Time')
        plt.title('Mean Travel Times Over Episodes (n = 3)')
        plt.legend()

        plt.savefig(save_to)
        plt.close()
        print(f"[SUCCESS] Travel times are saved to {save_to}")



    def retrieve_tt_per_kind(self):
        all_travel_times = {kc.TYPE_HUMAN: list(), kc.TYPE_MACHINE: list(), kc.TYPE_MACHINE_2: list()}
        for episode in self.saved_episodes:
            data_path = os.path.join(self.episodes_folder, f"ep{episode}.csv")
            data = pd.read_csv(data_path)
            kinds, travel_times = data[kc.AGENT_KIND], data[kc.TRAVEL_TIME]
            tt_per_kind =  {kc.TYPE_HUMAN: list(), kc.TYPE_MACHINE: list(), kc.TYPE_MACHINE_2: list()}
            for kind, tt in zip(kinds, travel_times):
                tt_per_kind[kind].append(tt)
            for kind in tt_per_kind.keys():
                all_travel_times[kind].append(tt_per_kind[kind])
        return all_travel_times


    
    def retrieve_mean_tt(self, all_travel_times):
        all_mean_tt, mean_human_tt, mean_machine_tt, mean_machine2_tt = list(), list(), list(), list()

        for idx, ep in enumerate(self.saved_episodes):
            human_tt = all_travel_times[kc.TYPE_HUMAN][idx]
            t_times = human_tt
            mean_human_tt.append(mean(human_tt))
            
            if ep >= self.mutation_time:
                machine_tt = all_travel_times[kc.TYPE_MACHINE][idx]
                t_times = t_times + machine_tt
                mean_machine_tt.append(mean(machine_tt))

            if ep >= self.second_mutation_time:
                machine2_tt = all_travel_times[kc.TYPE_MACHINE_2][idx]
                t_times = t_times + machine2_tt
                mean_machine2_tt.append(mean(machine2_tt))
            
            all_mean_tt.append(mean(t_times))

        return all_mean_tt, mean_human_tt, mean_machine_tt, mean_machine2_tt

####################
    

#################### TRAVEL TIME DISTRIBUTIONS
    
    def visualize_tt_distributions(self):
        save_to = make_dir(kc.PLOTS_FOLDER, kc.TT_DIST_PLOT_FILE_NAME)
    
        num_rows, num_cols = 2, 2
        fig, axes = plt.subplots(num_rows, num_cols, figsize=(self.multimode_width * num_cols, self.multimode_height * num_rows))
        fig.tight_layout(pad=5.0)

        if num_rows > 1:   axes = axes.flatten()   # Flatten axes

        # Plot mean rewards for each OD
        mean_tt_od = self.retrieve_mean_tt_per_od()
        sorted_keys = sorted(mean_tt_od.keys())
        for od in sorted_keys:
            axes[0].plot(self.saved_episodes, running_average(mean_tt_od[od], last_n=5), label=od)
        axes[0].axvline(x = self.mutation_time, label = 'Mutation Time', color = 'r', linestyle = '--')
        axes[0].axvline(x = self.second_mutation_time, label = 'Mutation Time 2', color = 'b', linestyle = '--')
        axes[0].set_xlabel('Episode')
        axes[0].set_ylabel('Mean Travel Time')
        axes[0].set_title('Mean Travel Times For OD Over Episodes (n = 5)')
        axes[0].legend()

        # Plot variance rewards for all, humans and machines
        all_travel_times = self.retrieve_tt_per_kind()
        all_var_tt, var_human_tt, var_machine_tt, var_machine2_tt  = self.retrieve_var_travel_times(all_travel_times)
        all_var_tt, var_human_tt, var_machine_tt, var_machine2_tt = running_average(all_var_tt, last_n=5), running_average(var_human_tt, last_n=5), running_average(var_machine_tt, last_n=5), running_average(var_machine2_tt, last_n=5)
        axes[1].plot(self.saved_episodes, all_var_tt, label="All")    # Before machines, it is just humans
        axes[1].plot(self.saved_episodes, var_human_tt, label="Humans")
        axes[1].plot(self.machine_episodes, var_machine_tt, label="Machines")
        axes[1].plot(self.machine2_episodes, var_machine2_tt, label="Disruptive")
        axes[1].axvline(x = self.mutation_time, label = 'Mutation Time 1', color = 'r', linestyle = '--')
        axes[1].axvline(x = self.second_mutation_time, label = 'Mutation Time 2', color = 'b', linestyle = '--')
        axes[1].set_xlabel('Episode')
        axes[1].set_ylabel('Variance TT')
        axes[1].set_title('Variance Travel Times Over Episodes (n = 5)')
        axes[1].legend()

        # Plot boxplot and violinplot for rewards
        ep_idx, ep = [(idx, ep) for idx, ep in enumerate(self.saved_episodes) if ep < self.mutation_time][-1]
        ep_idx2, ep2 = [(idx, ep) for idx, ep in enumerate(self.saved_episodes) if ep < self.second_mutation_time][-1]
        data_to_plot = [all_travel_times[kc.TYPE_HUMAN][ep_idx], all_travel_times[kc.TYPE_HUMAN][ep_idx2], all_travel_times[kc.TYPE_HUMAN][-1]]
        labels = [f'H #{ep}', f'H #{ep2}', 'H Final']

        axes[2].boxplot(data_to_plot, labels=labels, patch_artist=True)
        axes[2].set_ylabel('Travel Times')
        axes[2].set_title('Travel Time Distribution (Boxplot)')

        for label, data in zip(labels, data_to_plot):
            sns.kdeplot(data, ax=axes[3], label=label, alpha=0.3, fill=True, linewidth=0)
        axes[3].set_xlabel('Travel Times')
        axes[3].set_ylabel('Density (Probability)')
        axes[3].set_title('Travel Time Distribution (KDE)')
        axes[3].legend()

        #plt.show()
        plt.savefig(save_to)
        plt.close()
        print(f"[SUCCESS] Travel time distributions are saved to {save_to}")



    def retrieve_mean_tt_per_od(self):
        all_od_pairs = self.retrieve_all_od_pairs()
        all_mean_tt = {f"{od[0]} - {od[1]}" : list() for od in all_od_pairs}
        for idx, ep in enumerate(self.saved_episodes):
            episode_tts = {f"{od[0]} - {od[1]}" : list() for od in all_od_pairs}
            data_path = os.path.join(self.episodes_folder, f"ep{ep}.csv")
            episode_data = pd.read_csv(data_path)
            episode_origins, episode_destinations, travel_times = episode_data[kc.AGENT_ORIGIN], episode_data[kc.AGENT_DESTINATION], episode_data[kc.TRAVEL_TIME]
            for idx, tt in enumerate(travel_times):
                episode_tts[f"{episode_origins[idx]} - {episode_destinations[idx]}"].append(tt)
            for key in episode_tts.keys():
                all_mean_tt[key].append(mean(episode_tts[key]))
        return all_mean_tt
    


    def retrieve_var_travel_times(self, all_travel_times):
        all_var_tt, var_human_tt, var_machine_tt, var_machine2_tt = list(), list(), list(), list()

        for idx, ep in enumerate(self.saved_episodes):
            human_tt = all_travel_times[kc.TYPE_HUMAN][idx]
            travel_time = human_tt
            var_human_tt.append(variance(human_tt))
            
            if ep >= self.mutation_time:
                machine_tt = all_travel_times[kc.TYPE_MACHINE][idx]
                travel_time = travel_time + machine_tt
                var_machine_tt.append(variance(machine_tt))

            if ep >= self.second_mutation_time:
                machine2_tt = all_travel_times[kc.TYPE_MACHINE_2][idx]
                travel_time = travel_time + machine2_tt
                var_machine2_tt.append(variance(machine2_tt))
            
            all_var_tt.append(variance(travel_time))

        return all_var_tt, var_human_tt, var_machine_tt, var_machine2_tt

####################
    

#################### ACTIONS

    def visualize_actions(self):
        save_to = make_dir(kc.PLOTS_FOLDER, kc.ACTIONS_PLOT_FILE_NAME)

        all_actions, unique_actions = self.retrieve_actions()
        num_od_pairs = len(self.retrieve_all_od_pairs())
        
        # Determine the layout of the subplots (rows x columns)
        num_columns = self.default_num_columns
        num_rows = (num_od_pairs + num_columns - 1) // num_columns  # Calculate rows needed
        
        figure_size = (self.multimode_width * num_columns, self.multimode_height * num_rows)
        fig, axes = plt.subplots(num_rows, num_columns, figsize=figure_size)
        fig.tight_layout(pad=5.0)
        
        if num_rows > 1:   axes = axes.flatten()   # Flatten axes

        for idx, (od, actions) in enumerate(all_actions.items()):
            ax = axes[idx]
            for unique_action in unique_actions[od]:
                action_data = [ep_actions.get(unique_action, 0) for ep_actions in actions]
                action_data = running_average(action_data, last_n=5)
                ax.plot(self.saved_episodes, action_data, label=f"{unique_action}")

            ax.axvline(x = self.mutation_time, label = 'Mutation Time', color = 'r', linestyle = '--') 
            ax.axvline(x = self.second_mutation_time, label = 'Mutation Time 2', color = 'b', linestyle = '--')
            ax.set_title(f"Actions for {od} (n = 5)")
            ax.set_xlabel('Episodes')
            ax.set_ylabel('Population')
            ax.legend()

        # Hide unused subplots if any
        for ax in axes[idx+1:]:   ax.axis('off')    # Hide unused subplots if any

        plt.savefig(save_to)
        plt.close()
        print(f"[SUCCESS] Actions are saved to {save_to}")



    def retrieve_actions(self):
        all_od_pairs = self.retrieve_all_od_pairs()
        all_actions = {f"{od[0]} - {od[1]}" : list() for od in all_od_pairs}
        unique_actions = {f"{od[0]} - {od[1]}" : set() for od in all_od_pairs}
        for episode in self.saved_episodes:
            episode_actions = {f"{od[0]} - {od[1]}" : list() for od in all_od_pairs}
            data_path = os.path.join(self.episodes_folder, f"ep{episode}.csv")
            episode_data = pd.read_csv(data_path)
            episode_origins, episode_destinations, actions = episode_data[kc.AGENT_ORIGIN], episode_data[kc.AGENT_DESTINATION], episode_data[kc.ACTION]
            for idx, action in enumerate(actions):
                episode_actions[f"{episode_origins[idx]} - {episode_destinations[idx]}"].append(action)
            for key in episode_actions.keys():
                unique_actions[key].update(episode_actions[key])
                episode_actions[key] = Counter(episode_actions[key])
            for key in all_actions.keys():
                all_actions[key].append(episode_actions[key])
        return all_actions, unique_actions
            
####################
    

#################### ACTION SHIFTS
    
    def visualize_action_shifts(self):
        save_to = make_dir(kc.PLOTS_FOLDER, kc.ACTIONS_SHIFTS_PLOT_FILE_NAME)

        all_od_pairs = self.retrieve_all_od_pairs()
        
        # Determine the layout of the subplots (rows x columns)
        num_columns = self.default_num_columns
        num_rows = (len(all_od_pairs) + num_columns - 1) // num_columns  # Calculate rows needed
        
        figure_size = (self.multimode_width * num_columns, self.multimode_height * num_rows)
        fig, axes = plt.subplots(num_rows, num_columns, figsize=figure_size)
        fig.tight_layout(pad=5.0)
        
        if num_rows > 1:   axes = axes.flatten()   # Flatten axes

        for idx, od in enumerate(all_od_pairs):
            ax = axes[idx]
            origin, destination = od

            all_actions, unique_actions = self.retrieve_selected_actions(origin, destination)

            for action in unique_actions:
                action_data = [ep_counter[action] / sum(ep_counter.values()) for ep_counter in all_actions[kc.TYPE_HUMAN]]
                action_data = running_average(action_data, last_n=5)
                ax.plot(self.saved_episodes, action_data, label=f"Humans-{action}")

            for action in unique_actions: # Two loops just to make the plot legend alphabetical
                action_data = [ep_counter[action] / sum(ep_counter.values()) for ep_counter in all_actions[kc.TYPE_MACHINE]]
                action_data = running_average(action_data, last_n=5)
                ax.plot(self.machine_episodes, action_data, label=f"Machines-{action}")

            for action in unique_actions: # Two loops just to make the plot legend alphabetical
                action_data = [ep_counter[action] / sum(ep_counter.values()) for ep_counter in all_actions[kc.TYPE_MACHINE_2]]
                action_data = running_average(action_data, last_n=5)
                ax.plot(self.machine2_episodes, action_data, label=f"Disruptive-{action}")

            ax.axvline(x = self.mutation_time, label = 'Mutation Time', color = 'r', linestyle = '--')
            ax.axvline(x = self.second_mutation_time, label = 'Mutation Time 2', color = 'b', linestyle = '--')
            ax.set_xlabel('Episodes')
            ax.set_ylabel('Population')
            ax.set_title(f'Actions for {od} (Normalized by type population, n = 5)')
            ax.legend()

        for ax in axes[idx+1:]:   ax.axis('off')    # Hide unused subplots if any

        plt.savefig(save_to)
        plt.close()
        print(f"[SUCCESS] Actions shifts are saved to {save_to}")
        
    

    def retrieve_selected_actions(self, origin, destination):
        all_actions = {kc.TYPE_HUMAN: list(), kc.TYPE_MACHINE: list(), kc.TYPE_MACHINE_2: list()}
        unique_actions = set()
        for episode in self.saved_episodes:
            data_path = os.path.join(self.episodes_folder, f"ep{episode}.csv")
            data = pd.read_csv(data_path)
            data = data[(data[kc.AGENT_ORIGIN] == origin) & (data[kc.AGENT_DESTINATION] == destination)]
            kinds, actions = data[kc.AGENT_KIND], data[kc.ACTION]
            unique_actions.update(actions)
            actions_counters = {k : Counter() for k in set(kinds)}
            for kind, action in zip(kinds, actions):
                actions_counters[kind][action] += 1
            for kind in actions_counters.keys():
                all_actions[kind].append(actions_counters[kind])
        return all_actions, unique_actions
    
####################


#################### FLOWS
    
    def visualize_flows(self):
        save_to = make_dir(kc.PLOTS_FOLDER, kc.FLOWS_PLOT_FILE_NAME)

        ever_picked, all_selections = self.retrieve_flows()
        ever_picked = list(ever_picked)
        ever_picked.sort()
        
        plt.figure(figsize=(self.default_width, self.default_height))

        for pick in ever_picked:
            flow_data = [selections[pick] for selections in all_selections]
            flow_data = running_average(flow_data, last_n=5)
            plt.plot(self.saved_episodes, flow_data, label=pick)

        plt.axvline(x = self.mutation_time, label = 'Mutation Time', color = 'r', linestyle = '--')
        plt.axvline(x = self.second_mutation_time, label = 'Mutation Time 2', color = 'b', linestyle = '--')

        plt.xlabel('Episodes')
        plt.ylabel('Population')
        plt.title('Population in Routes Over Episodes (n = 5)')
        plt.legend()

        #plt.show()
        plt.savefig(save_to)
        plt.close()
        print(f"[SUCCESS] Flows are saved to {save_to}")



    def retrieve_flows(self):

        all_selections = list()
        ever_picked = set()

        for episode in self.saved_episodes:
            experience_data_path = os.path.join(self.episodes_folder, f"ep{episode}.csv")
            experience_data = pd.read_csv(experience_data_path)
            actions = experience_data[kc.SUMO_ACTION]

            ever_picked.update(actions)
            actions_counter = Counter(actions)
            all_selections.append(actions_counter)

        return ever_picked, all_selections
        
####################
    

#################### SIM LENGTH
    
    def visualize_sim_length(self):
        save_to = make_dir(kc.PLOTS_FOLDER, kc.SIMULATION_LENGTH_PLOT_FILE_NAME)

        sim_lengths = self.retrieve_sim_length()
        sim_lengths = running_average(sim_lengths, last_n = 10)

        plt.figure(figsize=(self.default_width, self.default_height))
        plt.plot(self.saved_episodes, sim_lengths, label="Simulation timesteps")
        plt.axvline(x = self.mutation_time, label = 'Mutation Time', color = 'r', linestyle = '--')
        plt.axvline(x = self.second_mutation_time, label = 'Mutation Time 2', color = 'b', linestyle = '--')
        plt.xlabel('Episode')
        plt.ylabel('Simulation Length')
        plt.title('Simulation Length Over Episodes (n = 10)')
        plt.legend()

        #plt.show()
        plt.savefig(save_to)
        plt.close()
        print(f"[SUCCESS] Simulation lengths are saved to {save_to}")



    def retrieve_sim_length(self):
        sim_lengths = list()
        with open(self.sim_length_file_path, "r") as file:
            lines = file.readlines()
            for line in lines:
                sim_lengths.append(int(line.strip()))
        return sim_lengths
    
####################


#################### LOSSES

    def visualize_losses(self):
        save_to = make_dir(kc.PLOTS_FOLDER, kc.LOSSES_PLOT_FILE_NAME)

        losses = self.retrieve_losses()
        losses = running_average(losses, last_n = 10)

        plt.figure(figsize=(self.default_width, self.default_height))
        plt.plot(losses)
        plt.xlabel('Training Progress')
        plt.ylabel('MSE Loss')
        plt.title('MSE Loss Over Training Progress (n = 10)')

        #plt.show()
        plt.savefig(save_to)
        plt.close()
        print(f"[SUCCESS] Losses are saved to {save_to}")



    def retrieve_losses(self):
        losses = list()
        with open(self.loss_file_path, "r") as file:
            lines = file.readlines()
            for line in lines:
                losses.append(float(line.strip()))
        return losses
    
####################


#################### HELPERS

    def retrieve_all_od_pairs(self):
        all_od_pairs = list()
        data_path = os.path.join(self.episodes_folder, f"ep{self.saved_episodes[0]}.csv")
        episode_data = pd.read_csv(data_path)
        episode_data = episode_data[[kc.AGENT_ORIGIN, kc.AGENT_DESTINATION]]
        for _, row in episode_data.iterrows():
            origin, destination = row[kc.AGENT_ORIGIN], row[kc.AGENT_DESTINATION]
            all_od_pairs.append((origin, destination))
        all_od_pairs = list(set(all_od_pairs))
        return all_od_pairs
    
####################