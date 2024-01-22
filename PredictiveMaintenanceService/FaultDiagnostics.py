import pandas as pd
import logging
import yaml
# from PredictiveMaintenanceService.observer_pattern import Event, Observer
from observer_pattern import Event, Observer
from datetime import datetime

#done
class FaultDiagnostic(Observer):
    def __init__(self):
        super().__init__()
        self.current_state = self.idle_state_fault
        self.fault_state_assessed = Event()
        self.data = None
        self.load_model_params()
        self.model_deployed = None
        self.models = {
            "battery": {"soc": self.calculate_soc, "soh": self.calculate_soh},
        }
        self.model_metric = {"battery": {"soc": 99, "soh": 90}} 
    
    def handle_event(self, data):
        self.data = data
        self.run()
        self.fault_state_assessed.emit(self.data)

    def run(self):
        """
        Executes the state transition loop.
        """
        logging.info("Fault Diagnostics initialized...")
        while self.current_state is not None:
            self.current_state = self.current_state()

    def load_model_params(self):
        # Load the parameters
        with open('C://Users/U/Documents/4.Semester/Masterarbeit/concept_implementation/PredictiveMaintenanceService/model_params.yaml', 'r') as file:
            self.model_params = yaml.safe_load(file)

    def calculate_soc(self):
        """
        Calculate the State of Charge (SoC) of the battery.
        """
        params = self.model_params[self.data["configuration"]["data_type"]][self.data["configuration"]["operational_condition"]]
        Vmin = params['Vmin']
        Vmax = params['Vmax']
        SoC = abs(((self.data["scale_value_Bat_Volt"] - Vmin) / (Vmax - Vmin))) * 100 # normally you would have to define the measure of interest 'scaled_Bat_Volt' somewhere else.
        return SoC
    
    def calculate_soh(self):
        """
        Calculate the State of Health (SoH) of the battery.
        """
        params = self.model_params[self.data["configuration"]["data_type"]][self.data["configuration"]["operational_condition"]]
        Vfull_original = params['Vfull_original']
        SoC = abs(((self.data["health_Bat_Volt"]) / (Vfull_original))) * 100 
        return SoC

    def idle_state_fault(self):
        if self.isModel():
            return self.deploy_model
        return self.idle_state_fault

    def deploy_model(self):
        logging.info("Model deployed.")
        self.model_deployed = list(self.models[self.data["configuration"]["data_type"]].values())[0]
        return self.diagnostic_state

    def diagnostic_state(self):
        if self.isHealth():
            return self.assessment_state
        elif ~self.isHealth():
            return self.fault_processing
        return None

    def fault_processing(self):
        if self.isFatal():
            self.failure_alarm()
        if self.isProcessed():
            return self.assessment_state
        return None
    
    def assessment_state(self):
        if self.isReport():
            return None
        return None

    def failure_alarm(self):
        logging.error("Fatal fault detected! Triggering alarm.")
        print("Alarm.")

    def generate_and_send_assessment_report(self):
        logging.info(f"Assessment report generated and sent. ")
        if self.data["health_status"]:
            self.data["fault_diagnostic_report"] = {"health_status": self.data["health_status"]}
            return True
        else: 
            self.data["fault_diagnostic_report"] = self.data["fault_processed"]
            return True

    def isModel(self):
        return self.models[self.data["configuration"]["data_type"]]

    def isHealth(self):
        self.data["health"] = self.model_deployed()
        self.data["health_status"] = list(self.model_metric[self.data["configuration"]["data_type"]].values())[0] < self.data["health"]
        return self.data["health_status"]
        
    def isFatal(self):
        # Determine if the anomaly is fatal
        return False

    def isProcessed(self):
        self.data["fault_processed"] = self.process_fault()
        return True

    def process_fault(self):
        return {
            "health_status": self.data["health_status"],
            "fault_time": datetime.now(),
            "fault_location": self.data["configuration"]["data_type"],
            "fault_severity": self.calc_severity()
        }
    
    def calc_severity(self):
        """ Calculate the severity rating """
        if not 0 <= self.data["health"] <= 100:
            raise ValueError("error.")
        severity = 5 - self.data["health"] // 20
        return severity

    def isReport(self):
        if self.generate_and_send_assessment_report():
            return True
        else:
            self.isReport()

    def get_data(self):
        return self.data
    