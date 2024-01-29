import pandas as pd
import logging
from datetime import datetime
from utilities.observer_pattern import Event, Observer

class DataAcquisition:
    def __init__(self):
        self.accumulated_data = None
        self.on_data_accessed = Event()

    def collect_data(self, entry, data_type):
        self.entry = entry
        df = pd.Series({"timestamp": self.entry.features["ml40::Time"].time,
                   "Bat_Volt": self.entry.features["ml40::Composite"].targets["Battery"].features["ml40::BatteryStatus"].voltage, 
                   "FuelPressure": self.entry.features["ml40::Composite"].targets["Fuel Filter"].features["ml40::Pressure"].pressure,
                   "RPM_Diesel": self.entry.features["ml40::Composite"].targets["Diesel Engine"].features["ml40::RotationalSpeed"].rpm})
        df["data_type"] = data_type # filter, battery
        df["datetime"] = datetime.fromtimestamp(int(df["timestamp"]))
        self.on_data_accessed.emit(df.copy())
        print("test")

    def store_data(self, df):
        if self.accumulated_data is None:
            self.accumulated_data = df
        else:
            self.accumulated_data = self.accumulated_data.append(df, ignore_index=True)


