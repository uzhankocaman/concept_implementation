class Prognostics:
    def __init__(self):
        self.current_state = self.idle_state_prognostics

    def transition(self, data):
        self.current_state = self.current_state(data)
        return self.current_state

    def idle_state_prognostics(self, data):
        if self.time_cycle_due():
            return self.prognostic_state
        return self.idle_state_prognostics

    def prognostic_state(self, data):
        degradation_trend, trend_analysis_result = self.predict_degradation_trend(data)
        if trend_analysis_result:
            return lambda _: self.rul_predict_state(degradation_trend)
        else:
            return self.idle_state_prognostics

    def rul_predict_state(self, degradation_trend):
        rul = self.estimate_rul(degradation_trend)
        return lambda _: self.assessment_state_prognostics(rul)

    def assessment_state_prognostics(self, rul):
        health_status = self.analyze_health_status(rul)
        report = self.generate_health_report(health_status)
        self.send_health_report(report)
        return self.idle_state_prognostics

    def time_cycle_due(self):
        return True

    def predict_degradation_trend(self, data):
        degradation_trend = "test"
        trend_analysis_result = True  
        return degradation_trend, trend_analysis_result

    def estimate_rul(self, degradation_trend):
        return 100

    def analyze_health_status(self, rul):
        return "Good"

    def generate_health_report(self, health_status):
        return "Health Report"

    def send_health_report(self, report):
        print("Sending report:", report)


