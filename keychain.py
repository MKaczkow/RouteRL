class Keychain:

    """
    This is where we store our file paths, parameter access keys and other constants reliably
    When change needed, just fix it here! Avoid hardcoding...
    """

    ################## RELATIVE FILE PATHS ####################

    PARAMS_PATH = "params.json"


    RECORDS_FOLDER = "training_records"
    EPISODES_LOGS_FOLDER = "episodes"
    MACHINES_LOG_FOLDER = "machines"
    HUMANS_LOG_FOLDER = "humans"
    SIMULATION_LOG_FOLDER = "simulation"

    SIMULATION_LENGTH_LOG_FILE_NAME = "simulation_length.txt"

    PLOTS_FOLDER = "plots"
    REWARDS_PLOT_FILE_NAME = "rewards.png"
    ONE_HUMAN_PLOT_FILE_NAME = "one_human.png"
    ONE_MACHINE_PLOT_FILE_NAME = "one_machine.png"
    FLOWS_PLOT_FILE_NAME = "flows.png"
    SIMULATION_LENGTH_PLOT_FILE_NAME = "simulation_length.png"
    
    ###########################################################
    
    

    
    ################ PARAMETER ACCESS KEYS ####################

    AGENTS_GENERATION_PARAMETERS = "agent_generation_parameters"
    TRAINING_PARAMETERS = "training_parameters"
    ENVIRONMENT_PARAMETERS = "environment_parameters"
    SIMULATION_PARAMETERS = "simulation_parameters"

    # Agent generation
    AGENTS_DATA_PATH = "agents_data_path"
    NUM_AGENTS = "num_agents"
    SIMULATION_TIMESTEPS = "simulation_timesteps"

    ACTION_SPACE_SIZE = "action_space_size"
    MACHINE_AGENT_PARAMETERS = "machine_agent_parameters"
    HUMAN_AGENT_PARAMETERS = "human_agent_parameters"

    MIN_ALPHA = "min_alpha"
    MAX_ALPHA = "max_alpha"
    MIN_EPSILON = "min_epsilon"
    MAX_EPSILON = "max_epsilon"
    MIN_EPS_DECAY = "min_eps_decay"
    MAX_EPS_DECAY = "max_eps_decay"
    GAMMA = "gamma"

    BETA = "beta"
    ALPHA = "alpha"

    # Training
    NUM_EPISODES = "num_episodes"

    # Environment
    TRANSPORT_PENALTY = "transport_penalty"

    # Simulation
    SUMO_TYPE = "sumo_type"
    SUMO_CONFIG_PATH = "sumo_config_path"
    CONNECTION_FILE_PATH = "connection_file_path"
    EDGE_FILE_PATH = "edge_file_path" 
    ROUTE_FILE_PATH = "route_file_path"
    ROUTES_XML_SAVE_PATH = "routes_xml_save_path"
    PATHS_SAVE_PATH = "paths_save_path"
    NUMBER_OF_PATHS = "number_of_paths"
    ORIGINS = "origins"
    DESTINATIONS = "destinations"

    # Recorder
    RECORDER_PARAMETERS = "recorder_parameters"
    REMEMBER_EVERY = "remember_every"
    RECORDER_MODE = "mode"
    TRACK_HUMAN = "track_human"
    TRACK_MACHINE = "track_machine"

    ###########################################################
    
    

    
    ####################### ELSE ##############################

    SMALL_BUT_NOT_ZERO = 1e-14

    SUMO_HOME = "SUMO_HOME"

    AGENT_ATTRIBUTES = "agent_attributes"
    
    # Common dataframe column headers
    AGENT_ID = "id"
    AGENT_ORIGIN = "origin"
    AGENT_DESTINATION = "destination"
    AGENT_START_TIME = "start_time"
    AGENT_TYPE = "agent_type"
    ACTION = "action"
    SUMO_ACTION = "sumo_action"
    REWARD = "reward"
    COST = "cost"
    Q_TABLE = "q_table"
    EPSILON = "epsilon"
    EPSILON_DECAY_RATE = "epsilon_decay_rate"
    DEPART_TIME = "depart_time"
    COST_TABLE = "cost_table"
    TRAVEL_TIME = "travel_time"
    HUMANS = "humans"
    MACHINES = "machines"
    ALL = "all"

    # Agent type encodings
    TYPE_HUMAN = "h"
    TYPE_MACHINE = "m"

    # Recorder modes
    PLOT_ONLY = "plot_only"
    SAVE_ONLY = "save_only"
    PLOT_AND_SAVE = "plot_and_save"

    ###########################################################