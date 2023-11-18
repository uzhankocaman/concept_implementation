import pandas as pd
import numpy as np
import time

from PredictiveMaintenanceService.DataAcquisition import DataAcquisition
from PredictiveMaintenanceService.DataProcessing import DataProcessing
from PredictiveMaintenanceService.Prognostics import Prognostics
from PredictiveMaintenanceService.FaultDiagnostics import FaultDiagnostics
from PredictiveMaintenanceService.HealthManagement import HealthManagement

from SensorSimulation.SimulateSensor import simulated_sensor

def main():
    data_acquisition = DataAcquisition()
    data_processing = DataProcessing()
    fault_diagnostics = FaultDiagnostics()
    prognostics_assessment = Prognostics()
    health_management = HealthManagement()


    file_path = "CAN_short_20220504_cleaned.xlsx"
    sensor_data_generator = simulated_sensor(file_path, 0)
    stored_data = pd.DataFrame()

    # Loop to simulate continuous data acquisition
    while True:
        raw_data, data_available = data_acquisition.access_data(sensor_data_generator)
        if not data_available:
            break
        else:
            data_acquisition.set_data(raw_data)
        processed_data = data_processing.process_data(stored_data) # change to row-wise processing?
    
    print("entering fault_diagnostic_assessment")
    for index, processed_datapoint in processed_data.iterrows():
        # # FAULT DIAGNOSTICS 
        fault_diagnostic_assessment = fault_diagnostics_system()
        fault_diagnostic_assessment(processed_datapoint)

if __name__ == '__main__':
    main()
