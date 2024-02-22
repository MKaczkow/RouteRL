import networkx as nx
import pandas as pd
import traci
import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup

from keychain import Keychain as kc
from services import SumoController
from utilities import path_generator
from utilities import list_to_string
from utilities import remove_double_quotes


class Simulator:

    """
    The interface between traffic simulator (SUMO, HihgEnv, Flow) and the environment
    """

    def __init__(self, params):

        self.sumo_controller = SumoController(params)

        self.routes_xml_save_path = params[kc.ROUTES_XML_SAVE_PATH]

        self.number_of_paths = params[kc.NUMBER_OF_PATHS]
        self.paths_save_path = params[kc.PATHS_SAVE_PATH]

        self.simulation_length = params[kc.SIMULATION_TIMESTEPS]
        self.beta = params[kc.BETA]

        # NX graph, built on a OSM map
        self.traffic_graph = self.generate_network(params[kc.CONNECTION_FILE_PATH], params[kc.EDGE_FILE_PATH], params[kc.ROUTE_FILE_PATH])

        # We keep origins and dests as dict {origin_id : origin_code}
        # Such as (0 : "279952229#0") and (1 : "279952229#0")
        # Keys are what agents know, values are what we use in SUMO
        self.origins = {i : origin for i, origin in enumerate(params[kc.ORIGINS])}
        self.destinations = {i : dest for i, dest in enumerate(params[kc.DESTINATIONS])}

        # We keep routes as dict {(origin_id, dest_id) : [list of nodes]}
        # Such as ((0,0) : [list of nodes]) and ((1,0) : [list of nodes])
        # In list of nodes, we use SUMO simulation ids of nodes
        self.routes = self.create_routes(self.origins, self.destinations)
        self.save_paths(self.routes)

        self.last_simulation_duration = 0



    def start_sumo(self):
        self.sumo_controller.sumo_start()

    def stop_sumo(self):
        self.sumo_controller.sumo_stop()

    def reset_sumo(self):
        self.sumo_controller.sumo_reset()


    
    def get_last_sim_duration(self):
        return self.last_simulation_duration

        

    def save_paths(self, routes):
        # csv file, for us
        paths_df = pd.DataFrame(columns = ["origin", "destination", "path"])
        for od, paths in routes.items():
            for path in paths:
                paths_df.loc[len(paths_df)] = [od[0], od[1], list_to_string(path, "-> ")]
        paths_df.to_csv(self.paths_save_path, index=True)
        print("[SUCCESS] Generated & saved %d paths to: %s" % (len(paths_df), self.paths_save_path))
        
        # XML file, for sumo
        with open(self.routes_xml_save_path, "w") as rou:
            print("""<routes>""", file=rou)
            for od, paths in routes.items():
                    for idx, path in enumerate(paths):
                        print(f'<route id="{od[0]}_{od[1]}_{idx}" edges="',file=rou)
                        print(list_to_string(path,separator=' '),file=rou)
                        print('" />',file=rou)
            print("</routes>", file=rou)
        


    def create_routes(self, origins, destinations):
        routes = dict()
        for origin_id, origin_sim_code in origins.items():
            for dest_id, dest_sim_code in destinations.items():
                route = self.find_best_paths(origin_sim_code, dest_sim_code, 'time')
                routes[(origin_id, dest_id)] = route
        return routes
    


    def find_best_paths(self, origin, destination, weight):
        paths = list()
        picked_nodes = set()

        for _ in range(self.number_of_paths):
            while True:
                path = path_generator(self.traffic_graph, origin, destination, weight, picked_nodes, self.beta)
                if path not in paths: break     # if path is not already generated, then break
            paths.append(path)
            picked_nodes.update(path)

        return paths



    def free_flow_time_finder(self, x, y, z, l):
        length=[]
        for route in range(len(x)):
            rou=[]
            for i in range(len(x[route])):
                if i < len(x[route]) - 1:
                    for k in range(len(y)):
                        if x[route][i] == y[k] and x[route][i + 1] == z[k]:
                            rou.append(l[k])
            length.append(sum(rou))
            #length.append(0)
        return length
    


    def calculate_free_flow_times(self):
        length = pd.DataFrame(self.traffic_graph.edges(data = True))
        time = length[2].astype('str').str.split(':',expand=True)[1]
        length[2] = time.str.replace('}','',regex=True).astype('float')

        free_flows_dict = dict()
        # Loop through the values in self.routes
        for od, route in self.routes.items():
            # Call free_flow_time_finder for each route
            free_flow = self.free_flow_time_finder(route, length[0], length[1], length[2])
            # Append the free_flow value to the list
            free_flows_dict[od] = free_flow

        return free_flows_dict



    def generate_network(self, connection_file, edge_file, route_file):
        # Connection file
        from_db, to_db = self.read_xml_file(connection_file, 'connection', 'from', 'to')
        from_to = pd.merge(from_db,to_db,left_index=True,right_index=True)
        from_to = from_to.rename(columns={'0_x':'From','0_y':'To'})
        
        # Edge file
        id_db, from_db = self.read_xml_file(edge_file, 'edge', 'id', 'from')

        id_name = pd.merge(from_db,id_db,right_index=True,left_index=True)

        id_name['0_x']=[remove_double_quotes(x) for x in id_name['0_x']]
        id_name['0_y']=[remove_double_quotes(x) for x in id_name['0_y']]
        id_name=id_name.rename(columns={'0_x':'Name','0_y':'ID'})
        
        # Route file
        with open(route_file, 'r') as f:
            data_rou = f.read()
        Bs_data_rou = BeautifulSoup(data_rou, "xml")

        # Extract <connection> elements with 'via' attribute
        rou = Bs_data_rou.find_all('edge', {'to': True})

        empty = [str(rou[x]) for x in range(len(rou))]

        id, length, speed = list(), list(), list()
        for x in range(len(empty)):
            root = ET.fromstring(empty[x])
            id.append(root.attrib.get('id'))
            length.append(root.find('.//lane').attrib.get('length'))
            speed.append(root.find('.//lane').attrib.get('speed'))
        
        id_db=pd.DataFrame(id)
        len_db=pd.DataFrame(length)
        speed_db=pd.DataFrame(speed)

        speed_name=pd.merge(speed_db,id_db,right_index=True,left_index=True)
        speed_name=speed_name.rename(columns={'0_x':'speed','0_y':'ID'})

        len_name=pd.merge(len_db,id_db,right_index=True,left_index=True)
        len_name=len_name.rename(columns={'0_x':'length','0_y':'ID'})

        id_name=pd.merge(len_name,id_name,right_on='ID',left_on='ID')
        id_name=pd.merge(speed_name,id_name,right_on='ID',left_on='ID')

        final=pd.merge(id_name,from_to,right_on='From',left_on='ID')
        final=final.drop(columns=['ID'])
        final=pd.merge(id_name,final,right_on='To',left_on='ID')
        final['time']=((final['length_x'].astype(float)/(final['speed_x'].astype(float)))/60)
        final=final.drop(columns=['ID','length_y','speed_y','speed_x','length_x'])
        traffic_graph = nx.from_pandas_edgelist(final, 'From', 'To', ['time'], create_using=nx.DiGraph())
    
        return traffic_graph
    


    def joint_action_to_sorted_stack(self, joint_action):
        sorted_joint_action = joint_action.sort_values(kc.AGENT_START_TIME, ascending=False)

        stack_bottom_placeholder = {kc.AGENT_START_TIME : -1}
        agents_stack = [stack_bottom_placeholder]

        for _, row in sorted_joint_action.iterrows():
            agents_stack.append(row)
        return agents_stack
    


    def run_simulation_iteration(self, joint_action):
        depart_id, depart_time, depart_id_set = list(), list(), set()
        agents_stack = self.joint_action_to_sorted_stack(joint_action)

        # Simulation loop
        while (len(depart_id) != joint_action.shape[0]):

            timestep = int(traci.simulation.getTime())

            # Add vehicles to the simulation
            while agents_stack[-1][kc.AGENT_START_TIME] == timestep:
                row = agents_stack.pop()
                action = row[kc.ACTION]
                vehicle_id = f"{row[kc.AGENT_ID]}"
                ori=row[kc.AGENT_ORIGIN]
                dest=row[kc.AGENT_DESTINATION]
                sumo_action = self.sumonize_action(ori, dest, action)
                traci.vehicle.add(vehicle_id, sumo_action)

            # Collect vehicles that have reached their destination
            departed = traci.simulation.getArrivedIDList() # returns a list of arrived vehicle ids
            departed = [int(value) for value in departed] # convert to int
            departed = [value for value in departed if (value not in depart_id_set)] # for some reason sometimes adds twice

            for value in departed:
                depart_id.append(value)
                depart_time.append(timestep)

            depart_id_set.update(depart_id)
            traci.simulationStep()
            

        self.last_simulation_duration = timestep
        travel_times_df = self.prepare_travel_times_df(depart_id, depart_time, joint_action)
        return travel_times_df
        
        

    def prepare_travel_times_df(self, depart_id, depart_time, joint_action):
        # Initiate the travel_time_df
        travel_time_df = pd.DataFrame({kc.AGENT_ID: depart_id, kc.DEPART_TIME: depart_time})

        # Merge the travel_time_df with the start_times_df for travel time calculation
        start_times_df = joint_action[[kc.AGENT_ID, kc.AGENT_START_TIME]]
        travel_time_df = pd.merge(left=start_times_df, right=travel_time_df, on=kc.AGENT_ID, how='left')
        #reward.fillna(value=timestep, inplace=True)

        # Calculate travel time
        travel_time_df[kc.TRAVEL_TIME] = (travel_time_df[kc.DEPART_TIME] - travel_time_df[kc.AGENT_START_TIME]) / 60

        # Retain only the necessary columns
        return travel_time_df[[kc.AGENT_ID, kc.TRAVEL_TIME]]


    
    def read_xml_file(self, file_path, element_name, attribute_name, attribute_name_2):
        with open(file_path, 'r') as f:
            data = f.read()
        Bs_data_con = BeautifulSoup(data, "xml")
        
        connections = Bs_data_con.find_all(element_name)

        empty=[]
        for x in range(len(connections)):
            empty.append(str(connections[x]))

        from_=[]
        to_=[]
        for x in range(len(empty)):
            root = ET.fromstring(empty[x])
            from_.append(root.attrib.get(attribute_name))
            to_.append(root.attrib.get(attribute_name_2))

        from_db=pd.DataFrame(from_)
        to_db=pd.DataFrame(to_)
        return from_db, to_db



    def sumonize_action(self, origin, destination, action):
        return f'{origin}_{destination}_{action}'
    