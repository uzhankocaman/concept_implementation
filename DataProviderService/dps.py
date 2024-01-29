from ml.ml40.features.functionalities.provides_machine_data import ProvidesMachineData
from utilities.observer_pattern import Event, Observer
import cantools
import can
import os
from pprint import pprint 
import sqlite3
import pandas as pd
import yaml
import time
import asyncio 
import sqlite3
import pandas as pd
import sqlite3
import pandas as pd
import sqlite3
import pandas as pd

class PhysicalTwinSimulation:
    def __init__(self):
        self.ready_to = Event() # Data Sharing Network
        self.config = self.load_config()
        self.db = cantools.database.load_file(self.config['database_path'])
        self.log_files_directory = self.config['log_files_directory']
        self.connection = self.config['connect']

    @staticmethod
    def load_config():
        with open('config.yaml', 'r') as file:
            return yaml.safe_load(file)
        
    def connect(self):
        if self.connection:
            self.access_canbus()

    def access_canbus(self):
        for file_name in os.listdir(self.log_files_directory):
            if file_name.endswith('.log'):
                self.gather_and_package_data(os.path.join(self.log_files_directory, file_name))

    def gather_and_package_data(self, log_file_path):
        # generate log file, package log data
        with open(log_file_path, 'r') as file:
            data_package = {}
            for i, line in enumerate(file, 1):
                try:
                    parts = line.strip().split(' ')
                    timestamp = parts[0]
                    # can_interface = parts[1]
                    frame_id, data = parts[2].split('#')
                    frame_id = int(frame_id, 16) 
                    data = bytes.fromhex(data.split(' ')[0]) 
                    data_package[frame_id] = {
                            "timestamp": timestamp,
                            # "interface": can_interface,
                            # "frame_id": frame_id,
                            "data": data
                        }
                except:
                    break
                if (((i % 6) == 0) & (len(data_package) == 6)):
                    self.ready_to.emit(data_package) # transmit data package
                    data_package = {}

class DataAcquisitionGateway(Observer):
    def __init__(self):
        self.on_acquisition = Event()
        self.config = self.load_config()
        self.db = cantools.database.load_file(self.config['database_path'])

    @staticmethod
    def load_config():
        with open('config.yaml', 'r') as file:
            return yaml.safe_load(file)
        
    def handle_event(self, data_package): # communicate_through_api
        decoded_package = self.decode_data(data_package)
        aggregated_data = self.standardize_data(decoded_package)
        self.on_acquisition.emit(aggregated_data)
        aggregated_data = {}

    def decode_data(self, data_package):
        decoded_package = {}
        for key, value in data_package.items():
            try:
                decoded_data = self.db.decode_message(key, value["data"])
                decoded_package["timestamp"] = data_package[key]["timestamp"]
                decoded_package[key] = decoded_data
            except:
                break
        return decoded_package

    def standardize_data(self, decoded_package):
        aggregated_data = {}
        for key, value in decoded_package.items():
            if key != "timestamp":
                for skey, svalue in value.items():
                    aggregated_data[skey] = svalue
            else:
                aggregated_data["timestamp"] = float("{:.2f}".format(float(decoded_package['timestamp'].strip('()')))) 
        return aggregated_data 

class InformationGateway(Observer):
    def __init__(self):
        self.data = None
        self.callback = None
        self.db_file_path = "C:/Users/U/Documents/4.Semester/Masterarbeit/concept_implementation/data/can_data_processed_23112023.db"
        self.conn = sqlite3.connect(self.db_file_path)

    def handle_event(self, data):
        self.data = data
        if self.callback:
            self.callback(self.data)

    def register_callback(self, callback_function):
        self.callback = callback_function

    def get_data(self):
        return self.data

    def read_db(self):
        for i in range(10000):
            query = f"SELECT * FROM ProcessedCANData LIMIT 1 OFFSET {i}"
            df = pd.read_sql_query(query, self.conn)
            self.callback(df.to_dict('records')[0])

    def __del__(self):
        self.conn.close()

class DataProviderService():
    def __init__(self, name="", identifier=""):
        self.MachineData = {}
        self.physical_twin = PhysicalTwinSimulation()
        self.data_gateway = DataAcquisitionGateway()
        self.physical_twin.ready_to.subscribe(self.data_gateway)
        self.information_gateway = InformationGateway()
        self.information_gateway.register_callback(self.getMachineData)
        self.data_gateway.on_acquisition.subscribe(self.information_gateway)
        self.physical_twin.connect()
        # self.information_gateway.read_db()
        self.db_file_path = "C:/Users/U/Documents/4.Semester/Masterarbeit/concept_implementation/data/can_data_processed_23112023.db"
        

    def getMachineData(self, data=None):
        i = 1
        self.conn = sqlite3.connect(self.db_file_path)
        query = f"SELECT * FROM ProcessedCANData LIMIT 1 OFFSET {i}"
        df = pd.read_sql_query(query, self.conn)
        data = df.to_dict('records')[0]
        self.MachineData["timestamp"] = data["timestamp"]
        # self.MachineData["Supply_Press"] = data["Supply_Press"]
        # self.MachineData["RetFilt_Press"] = data["RetFilt_Press"]
        # self.MachineData["DrFor_Press"] = data["DrFor_Press"]
        # self.MachineData["DrBack_Press"] = data["DrBack_Press"]
        # self.MachineData["Cab_Angle"] = data["Cab_Angle"]
        # self.MachineData["FrameLR_Angle"] = data["FrameLR_Angle"]
        # self.MachineData["FrameFB_Angle"] = data["FrameFB_Angle"]
        # self.MachineData["WorkPump_Press"] = data["WorkPump_Press"]
        # self.MachineData["WorkPump_Q"] = data["WorkPump_Q"]
        # self.MachineData["HeadPump_Angle"] = data["HeadPump_Angle"]
        # self.MachineData["CraneSwivel_Angle"] = data["CraneSwivel_Angle"]
        self.MachineData["RPM_Diesel"] = data["RPM_Diesel"]
        # self.MachineData["Cool_Temp"] = data["Cool_Temp"]
        # self.MachineData["Oil_Temp"] = data["Oil_Temp"]
        # self.MachineData["Amb_Temp"] = data["Amb_Temp"]
        self.MachineData["FuelPressure"] = data["FuelPressure"]
        # self.MachineData["ChargedAir_Press"] = data["ChargedAir_Press"]
        self.MachineData["Bat_Volt"] = data["Bat_Volt"]
        # self.MachineData["Oil_Press"] = data["Oil_Press"]
        # self.MachineData["Engine_Load"] = data["Engine_Load"]
        # self.MachineData["RPM_DriveMot"] = data["RPM_DriveMot"]
        # self.MachineData["Speed"] = data["Speed"]
        # self.MachineData["Steering_Angle"] = data["Steering_Angle"]
        # self.MachineData["Drive_Dir"] = data["Drive_Dir"]
        i = i + 1
        return self.MachineData.values()
        
# machine_data_provider = DataProviderService()
# asyncio.run(machine_data_provider.getMachineData())

# machine_data_provider = DataProviderService()
# machine_data_provider.getMachineData()