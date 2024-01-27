import pandas as pd
import logging
from utilities.observer_pattern import Event, Observer

class DataAcquisition:
    def __init__(self):
        self.accumulated_data = None
        self.on_data_accessed = Event()

    def collect_data(self, entry, data_type):
        df = entry #process to get desired format
        df["data_type"] = data_type # filter, battery
        self.on_data_accessed.emit(df.copy())
        print("test")

    def store_data(self):
        pass

