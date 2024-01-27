import pandas as pd
import logging
from observer_pattern import Event, Observer

class DataAcquisition:
    def __init__(self):
        self.accumulated_data = None
        self.on_data_accessed = Event()
    def collect_data(self, entry):
        df = entry
        self.on_data_accessed.emit(entry)

    def store_data(self):
        pass

