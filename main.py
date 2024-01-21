import pandas as pd
import numpy as np
import time
import logging

from PredictiveMaintenanceService.DataAcquisition import DataAcquisition
from PredictiveMaintenanceService.DataProcessing import DataProcessing
from PredictiveMaintenanceService.Prognostics import Prognostics
from PredictiveMaintenanceService.FaultDiagnostics import FaultDiagnostics
from PredictiveMaintenanceService.HealthManagement import HealthManagement

from MaintenanceManagementService.MaintenanceManagementSystem import (
    MaintenanceManagementService,
)

from SensorSimulation.SimulateSensor import simulated_sensor

logging.basicConfig(level=logging.INFO)


def main():
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
