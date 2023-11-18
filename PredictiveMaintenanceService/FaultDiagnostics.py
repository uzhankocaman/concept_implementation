import pandas as pd
class FaultDiagnostics:
    def __init__(self):
        self.current_state = self.idle_state_fault

    def transition(self, data):
        while True:
            self.current_state = self.current_state(data)
            if self.current_state is self.idle_state_fault:
                break

    def idle_state_fault(self, data):
        if self.event_detected(data):
            return self.diagnostic_state
        return self.idle_state_fault

    def diagnostic_state(self, data):
        if self.fault_detection(data):
            return self.fault_processing_state
        return self.idle_state_fault

    def fault_processing_state(self, data):
        fault_time = self.alarm(data)
        fault_location = self.fault_isolation(data)
        fault_severity = self.fault_identification(data)
        return lambda _: self.assessment_state_fault(fault_time, fault_location, fault_severity)

    def assessment_state_fault(self, fault_time, fault_location, fault_severity):
        report = self.report_generate(fault_time, fault_location, fault_severity)
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
        return data["MaschineStatus.DieselFuellstand"] < 9999

    def alarm(self, data):
        # alarm/notification
        print("Fault detected!")
        return {"fault_time": "11/13/2023 17:39"}

    def fault_isolation(self, data):
        return {"fault_location": "Diesel Fuellstand"}

    def fault_identification(self, data):
        return {"fault_severity": "Level 4/5"}

    def report_generate(self, fault_time, fault_location, fault_severity):
        """
        Generate a report based on the fault information
        """
        return pd.DataFrame.from_dict(self, fault_time | fault_location | fault_severity, orient='index')

    def report_send(self, report):
        """
        Send the report to the health management system.
        """
        #health_management.receive_report(report)

# Example usage of FaultDiagnostics class
fault_diagnostics_system = FaultDiagnostics()
sensor_data = {"MaschineStatus.DieselFuellstand": 9998}  # Example data
fault_diagnostics_system.transition(sensor_data)
