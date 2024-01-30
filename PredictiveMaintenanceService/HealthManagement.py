# {'health_status': False, 'fault_time': datetime.datetime(2024, 1, 22, 8, 25, 2, 524487), 'fault_location': 'battery', 'fault_severity': 1.0}
# {'health_status': True}
from DataProviderService.observer_pattern import Observer, Event
import pandas as pd
import logging
import time
# from DataAcquisition import DataAcquisition
# from DataProcessing import DataProcessing
# from StateAdaptation import StateAdaptation
# from Prognostics import Prognostics
# from FaultDiagnostics import FaultDiagnostic
import numpy as np
import sqlite3

class HealthManagement(Observer):
    def __init__(self):
        super().__init__()
        self.data = {}
        self.reports = {}
        self.i = 0
        self.advisory_generated = False
        self.assessments_processed = False
        self.health_management_complete = Event()

    def handle_event(self, data):
        self.data[self.i] = data
        self.i += 1
        if self.is_ready_to_transmit_advisory():
            self.run()
            self.i = 0
            self.data = {}
            self.reports = {}
        else:
            # If not ready, continue waiting or perform other checks
            logging.info("Waiting for conditions to be met to transmit advisory.")
            time.sleep(0.1)

    def run(self):
        self.process_assessments()
        self.integrate_information()
        self.generate_advisory()
        self.transmit_advisory()
        print("finish")

    def is_ready_to_transmit_advisory(self):
        if self.i >= 2: 
            return True
        else:
            return False

    def process_assessments(self):
        self.organize_data()
        logging.info("Assessments processed and organized.")
    
    def organize_data(self):
        self.organized_data = {}
        for index in range(self.i):
            if np.sum(self.data[index].keys() == 'fault_diagnostic_report'):
                entry = self.data[index]
                self.organized_data = {
                    "datetime": entry["datetime"],
                    "data_type": entry["configuration"]["data_type"],
                    "operational_condition": entry["configuration"]["operational_condition"],
                    "fault_diagnostic_health_status": entry["fault_diagnostic_report"].get("health_status", None),
                    "fault_location": entry["fault_diagnostic_report"].get("fault_location", None),
                    "fault_severity": entry["fault_diagnostic_report"].get("fault_severity", None),
                    # "prognostic_status": entry["prognostics_report"].get("prognostic_status", None),
                }
    
    def integrate_information(self):
        # Concatenate the organized data into one dictionary.
        self.integrated_data = self.organized_data
        logging.info("Information from assessments integrated into a single dictionary.")

    def generate_advisory(self):
        self.advisory = self.create_advisory_based_on_data()
        logging.info("Advisory generated based on integrated data.")

    def create_advisory_based_on_data(self):
        advisories = {
            ('battery', 'engine_running'): "health problem",
            ('battery', 'engine_not_running'): "charging problem",
            ('filter', int): "high pressure detected",
        }
        if self.integrated_data['data_type'] == 'battery':
            condition_key = (self.integrated_data['data_type'], self.integrated_data.get('operational_condition'))
        if self.integrated_data['data_type'] == 'filter':
            condition_key = (self.integrated_data['data_type'], type(self.integrated_data["fault_severity"]))
        analysis = advisories.get(condition_key, "Status normal.")
        self.integrated_data["analysis"] = analysis

    def transmit_advisory(self):
        self.health_management_complete.emit(self.integrated_data)
        logging.info("Advisory transmitted to the next class.")
        self.data.clear()
        self.organized_data.clear()
        self.integrated_data.clear()
        self.i = 0

# data_acquisition = DataAcquisition()
# data_processor = DataProcessing()
# state_adaptation = StateAdaptation()
# fault_diagnostic = FaultDiagnostic()
# prognostic = Prognostics()
# health_management = HealthManagement()

# data_acquisition.on_data_accessed.subscribe(data_processor)

# data_processor.on_data_processed.subscribe(state_adaptation)

# state_adaptation.on_state_assessed.subscribe(fault_diagnostic)
# state_adaptation.on_state_assessed.subscribe(prognostic)

# fault_diagnostic.fault_state_assessed.subscribe(health_management)
# prognostic.prognostic_state_assessed.subscribe(health_management)

# db_file_path = "C:/Users/U/Documents/4.Semester/Masterarbeit/concept_implementation/data/can_data_processed_23112023.db"
# conn = sqlite3.connect(db_file_path)
# query = "SELECT * FROM ProcessedCANData"
# df_raw = pd.read_sql_query(query, conn)
# conn.close()

# file_path='PredictiveMaintenanceService/test.xlsx'
# df_raw = pd.read_excel(file_path)
# for i in range(len(df_raw)):
#     df_processed = df_raw.loc[df_raw.index[i]]   
#     # print(df_processed)
#     print("battery KKK")
#     data_acquisition.collect_data(df_processed, 'battery')
#     print("filter KKK")
#     data_acquisition.collect_data(df_processed, "filter")

# df_processed = df_raw.loc[df_raw.index[0]]  
# data_acquisition.collect_data(df_processed, 'battery') 