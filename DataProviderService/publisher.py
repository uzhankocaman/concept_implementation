import paho.mqtt.client as mqtt
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
import paho.mqtt.client as mqtt
import json
import base64

broker_address = "localhost"
port = 1883
topic = "test/topic"


def on_publish(client, userdata, result):
    print("Data published \n")
    pass


client = mqtt.Client("Publisher")
client.on_publish = on_publish
client.connect(broker_address, port)


class PhysicalTwinSimulation:
    def __init__(self):
        # self.ready_to = Event() # Data Sharing Network
        self.config = self.load_config()
        # self.db = cantools.database.load_file(self.config['database_path'])
        self.log_files_directory = self.config["log_files_directory"]
        self.connection = self.config["connect"]
        # self.connection = True
        self.j = 0

    @staticmethod
    def load_config():
        with open("config.yaml", "r") as file:
            return yaml.safe_load(file)

    # def connect(self):
    #     if self.connection:
    #         self.access_canbus()

    def access_canbus(self):
        # i = 0
        for file_name in os.listdir(self.log_files_directory):
            if file_name.endswith(".log"):
                self.gather_and_package_data(
                    os.path.join(self.log_files_directory, file_name)
                )
                # i = i + 1

    def gather_and_package_data(self, log_file_path):
        # generate log file, package log data
        with open(log_file_path, "r") as file:
            data_package = {}
            for i, line in enumerate(file, 1):
                try:
                    parts = line.strip().split(" ")
                    timestamp = parts[0]
                    # can_interface = parts[1]
                    frame_id, data = parts[2].split("#")
                    frame_id = int(frame_id, 16)
                    data = bytes.fromhex(data.split(" ")[0])
                    data_package[frame_id] = {
                        "timestamp": timestamp,
                        # "interface": can_interface,
                        # "frame_id": frame_id,
                        "data": data,
                    }
                except:
                    break
                if ((i % 6) == 0) & (len(data_package) == 6):
                    self.send_data(data_package)  # transmit data package
                    data_package = {}

    def send_data(self, data_package):
        # if self.j == 0: # Testing purposes
        for key, value in data_package.items():
            value["data"] = base64.b64encode(value["data"]).decode("utf-8")
        message = json.dumps(data_package)
        client.publish(topic, message)


virtual_twin = PhysicalTwinSimulation()
virtual_twin.access_canbus()
