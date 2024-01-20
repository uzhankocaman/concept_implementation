import pandas as pd
import time


# SENSOR BEHAVIOR SIMULATION
def simulated_sensor(file_path, transmission_interval=0):
    data = pd.read_excel(file_path)
    data_records = data.to_dict("records")
    for record in data_records:
        yield record
        time.sleep(transmission_interval)
