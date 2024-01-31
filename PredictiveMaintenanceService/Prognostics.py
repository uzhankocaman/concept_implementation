from datetime import datetime
from utilities.observer_pattern import Event, Observer
import time


# done
class Prognostics(Observer):
    def __init__(self):
        super().__init__()
        self.current_state = self.check_model_state
        self.report_callback = None
        self.data = None
        self.prognostic_state_assessed = Event()

    def handle_event(self, data):
        self.data = data
        self.run()

    def run(self):
        """
        Executes the state transition.
        """
        data = self.data
        max_iterations = 100
        for _ in range(max_iterations):
            new_state = self.current_state(data)
            if new_state is None or new_state == self.current_state:
                break
            self.current_state = new_state
        self.prognostic_state_assessed.emit(self.data["prognostics_report"])

    def check_model_state(self, data):
        """
        Check if the model exists to process the data.
        """
        if self.is_model():
            return self.detect_degradation_state
        self.data["prognostics_report"] = {"prognostic_status": "model_not_found"}
        return None  # Terminate if no model is available

    def detect_degradation_state(self, data):
        """
        Detect degradation.
        """
        if self.is_degradation(data):
            return self.predict_rul_state
        return self.assess_system_health_state

    def predict_rul_state(self, data):
        """
        Predict the Remaining Useful Life (RUL) of the system.
        """
        rul = self.estimate_rul(data)
        self.rul = rul
        return self.assess_system_health_state

    def assess_system_health_state(self, data):
        """
        Assess the overall system health based on RUL stored from the previous state.
        """
        report = self.report_generate(data)
        self.report_send(report)
        return None  # End

    def is_model(self):
        time.sleep(0.1)
        return False

    def is_degradation(self, data):
        pass

    def estimate_rul(self, data):
        pass

    def analyze_health_status(self, rul):
        pass

    def report_generate(self, health_status):
        pass

    def report_send(self, report):
        pass

    def load_model(self):
        """
        Load the predictive model.
        """
        self.model_last_updated = datetime.now()

    def update_model(self):
        """
        Update the predictive model from an external source.
        """
        self.model_last_updated = datetime.now()
