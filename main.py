import pandas as pd
import numpy as np
import time
import logging

from PredictiveMaintenanceService.DataAcquisition import DataAcquisition
from PredictiveMaintenanceService.DataProcessing import DataProcessing
from PredictiveMaintenanceService.StateAdaptation import StateAdaptation
from PredictiveMaintenanceService.Prognostics import Prognostics
from PredictiveMaintenanceService.FaultDiagnostics import FaultDiagnostic
from PredictiveMaintenanceService.HealthManagement import HealthManagement

from MaintenanceManagementService.MaintenanceManagementSystem import MaintenanceManagementService

from SensorSimulation.SimulateSensor import simulated_sensor

logging.basicConfig(level=logging.INFO)


def main():
    data_acquisition = DataAcquisition()
    data_processor = DataProcessing()
    state_adaptation = StateAdaptation()
    fault_diagnostic = FaultDiagnostic()
    prognostic = Prognostics()
    health_management = HealthManagement()

    data_acquisition.on_data_accessed.subscribe(data_processor)

    data_processor.on_data_processed.subscribe(state_adaptation)

    state_adaptation.on_state_assessed.subscribe(fault_diagnostic)
    state_adaptation.on_state_assessed.subscribe(prognostic)

    fault_diagnostic.fault_state_assessed.subscribe(health_management)
    prognostic.prognostic_state_assessed.subscribe(health_management)

    file_path='PredictiveMaintenanceService/test.xlsx'
    df_raw = pd.read_excel(file_path)
    for i in range(len(df_raw)):
        df_processed = df_raw.loc[df_raw.index[i]]   
        # print(df_processed)
        print("battery KKK")
        data_acquisition.collect_data(df_processed, 'battery')
        print("filter KKK")
        data_acquisition.collect_data(df_processed, "filter")
    # mms = MaintenanceManagementService()
    # mms.run()
    
    # def handle_report(report):
    #     health_management.receive_report(report)

    # def send_report(report):
    #     maintenance_service.receive_advisory(report)

    # data_acquisition = DataAcquisition()
    # data_processing = DataProcessing()
    # fault_diagnostics = FaultDiagnostics(handle_report)
    # prognostics_assessment = Prognostics(handle_report)
    # health_management = HealthManagement(send_report)

    # maintenance_service = MaintenanceServiceSystem()

    # file_path = "data/CAN_short_20220504.xlsx"
    # sensor_data_generator = simulated_sensor(file_path, 0)
    # while True:
    #     raw_data = data_acquisition.access_data(sensor_data_generator)
    #     if (
    #         raw_data is None
    #     ):  # migrate this to acces_data by waiting until data is available, try eliminate while True.
    #         print("No raw data available")
    #         break
    #     processed_data = data_processing.process_data(raw_data)
    #     fault_diagnostics.run(processed_data)
    #     # prognostics_assessment.run(processed_data)
    #     health_management.process_reports()
    #     maintenance_service.run()


if __name__ == "__main__":
    main()
