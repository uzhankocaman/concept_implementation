import pandas as pd
import logging

#TODO: if no fault (and event) is detected, no report is generated. 
#      instead, generate a report that indicates a good state
class FaultDiagnostics:
    def __init__(self, report_callback):
        self.current_state = self.idle_state_fault
        self.report_callback = report_callback

    def run(self, data):
        """
        executes the state transition
        """
        logging.info("Fault Diagnostics...")
        while True:
            self.current_state = self.current_state(data)
            if self.current_state == self.idle_state_fault:
                break

    def idle_state_fault(self, data):
        if self.event_detected(data):
            return self.diagnostic_state
        return self.idle_state_fault

    def diagnostic_state(self, data):
        if self.fault_detection(data): # empty dataframe returns when no fault detected.
            return self.fault_processing_state
        return self.idle_state_fault

    def fault_processing_state(self, data):
        fault_time = self.alarm(data)
        fault_location = self.fault_isolation(data)
        fault_severity = self.fault_identification(data)    
        return lambda _: self.assessment_state_fault(data, fault_time, fault_location, fault_severity)

    def assessment_state_fault(self, data, fault_time, fault_location, fault_severity):
        report = self.report_generate(data, fault_time, fault_location, fault_severity)
        self.report_send(report)
        return self.idle_state_fault

    def event_detected(self, data):
        """
        check if data is available
        """
        return data is not None

    def fault_detection(self, data):
        """
        check if data exceeds/deceeds certain threshold
        """
        return True # data["MaschineStatus.DieselFuellstand"].values < 9999

    def alarm(self, data):
        # alarm/notification
        print("Fault detected!")
        return {"fault_time": "11/13/2023 17:39"}

    def fault_isolation(self, data):
        return {"fault_location": "Diesel Fuellstand", "fault_value": data["MaschineStatus.DieselFuellstand"]}

    def fault_identification(self, data):
        return {"fault_severity": "Level 4/5"}

    def report_generate(self, data, fault_time, fault_location, fault_severity):
        """
        Generate a report based on the fault information
        """
        report = fault_time | fault_location | fault_severity 
        return data.assign(**report)

    def report_send(self, report):
        """
        Send the report to the health management system.
        """
        self.report_callback(report)

