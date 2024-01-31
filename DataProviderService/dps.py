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
import math
import paho.mqtt.client as mqtt
import json
import base64
from pandas import Timestamp

broker_address = "localhost"
port = 1883
topic = "test/topic"


class DataAcquisitionGateway:
    def __init__(self, can_encoder):
        self.on_acquisition = Event()
        # self.config = self.load_config()
        self.db = cantools.database.load_file(can_encoder)
        self.client = mqtt.Client("Subscriber")
        self.client.on_message = self.on_message
        self.client.connect(broker_address, port)
        self.client.subscribe(topic)
        self.start_listening()

    def on_message(self, client, userdata, message):  # communicate_through_mqtt
        payload = str(message.payload.decode("utf-8"))
        data_package_loaded = json.loads(payload)
        data_package = {}
        for key, value in data_package_loaded.items():
            data_package[int(key)] = value

        for key, value in data_package.items():
            value["data"] = base64.b64decode(value["data"])
        decoded_package = self.decode_data(data_package)
        aggregated_data = self.standardize_data(decoded_package)
        self.on_acquisition.emit(aggregated_data)

    def decode_data(self, data_package):
        decoded_package = {}
        for key, value in data_package.items():
            try:
                decoded_data = self.db.decode_message(int(key), value["data"])
                decoded_package["timestamp"] = data_package[int(key)]["timestamp"]
                decoded_package[int(key)] = decoded_data
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
                aggregated_data["timestamp"] = float(
                    "{:.2f}".format(float(decoded_package["timestamp"].strip("()")))
                )
        return aggregated_data

    def start_listening(self):
        self.client.loop_start()


class InformationGateway(Observer):
    def __init__(self, db_file_path):
        self.last_data = None
        self.callback = None
        self.db_file_path = db_file_path
        self.conn = sqlite3.connect(self.db_file_path)
        self.MachineData = {}
        # Testing:
        self.df = pd.read_excel(
            "C:/Users/U/Documents/4.Semester/Masterarbeit/concept_implementation/DataProviderService/test_sample.xlsx"
        )
        self.i = 67

    def handle_event(self, data):
        self.last_data = data
        # self.store_sensor_data(data)

    # def register_callback(self, callback_function):
    #     self.callback = callback_function

    # def get_data(self):
    #     return self.data

    def store_sensor_data(self, data):
        serialized_data = json.dumps(data)

        self.conn.execute(
            """CREATE TABLE IF NOT EXISTS SensorData
                            (ID INTEGER PRIMARY KEY AUTOINCREMENT,
                            Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                            Data TEXT)"""
        )

        query = "INSERT INTO SensorData (Data) VALUES (?)"
        self.conn.execute(query, (serialized_data,))
        self.conn.commit()

    def store_maintenance_data(self, data):
        def default_serializer(obj):
            if isinstance(obj, Timestamp):
                return obj.isoformat()  # Convert Timestamp to ISO 8601 string

        serialized_data = json.dumps(data, default=default_serializer)

        self.conn.execute(
            """CREATE TABLE IF NOT EXISTS MaintenanceData
                            (ID INTEGER PRIMARY KEY AUTOINCREMENT,
                            Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                            Data TEXT)"""
        )

        query = "INSERT INTO MaintenanceData (Data) VALUES (?)"
        self.conn.execute(query, (serialized_data,))
        self.conn.commit()

    def read_db(self, i):
        # Read desired data from database, adjusted for specific need
        query = f"SELECT * FROM ProcessedCANData LIMIT 1 OFFSET {i}"
        df = pd.read_sql_query(query, self.conn)
        return df.to_dict("records")[0]

    def get_data(self):
        # Implement logic to get the desired data
        # if True: # Testing purposes
        #     self.MachineData = list(self.df.iloc[self.i][["timestamp", "RPM_Diesel", "FuelPressure", "Bat_Volt"]])
        #     self.i = self.i + 1
        #     if not any(math.isnan(item) for item in self.MachineData):
        #         print("=====")
        #         print(self.i)
        #         print("=====")
        #         return self.MachineData
        #     return None
        if self.last_data is not None and not any(
            math.isnan(value)
            for value in self.last_data.values()
            if isinstance(value, float)
        ):
            self.MachineData["timestamp"] = self.last_data["timestamp"]
            self.MachineData["RPM_Diesel"] = self.last_data["RPM_Diesel"]
            self.MachineData["FuelPressure"] = self.last_data["FuelPressure"]
            self.MachineData["Bat_Volt"] = self.last_data["Bat_Volt"]
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
            # self.MachineData["Cool_Temp"] = data["Cool_Temp"]
            # self.MachineData["Oil_Temp"] = data["Oil_Temp"]
            # self.MachineData["Amb_Temp"] = data["Amb_Temp"]
            # self.MachineData["ChargedAir_Press"] = data["ChargedAir_Press"]
            # self.MachineData["Oil_Press"] = data["Oil_Press"]
            # self.MachineData["Engine_Load"] = data["Engine_Load"]
            # self.MachineData["RPM_DriveMot"] = data["RPM_DriveMot"]
            # self.MachineData["Speed"] = data["Speed"]
            # self.MachineData["Steering_Angle"] = data["Steering_Angle"]
            # self.MachineData["Drive_Dir"] = data["Drive_Dir"]
            self.last_data = None
            return self.MachineData.values()
        return None

    def __del__(self):
        self.conn.close()


class DataProviderService:
    def __init__(self):
        self.config = self.load_config()
        self.MachineData = {}
        self.data_gateway = DataAcquisitionGateway(self.config["can_encoder"])
        self.information_gateway = InformationGateway(self.config["db_file_path"])
        self.data_gateway.on_acquisition.subscribe(self.information_gateway)

    @staticmethod
    def load_config():
        with open("config.yaml", "r") as file:
            return yaml.safe_load(file)


# dps = DataProviderService()

# dps.information_gateway.get_data()
