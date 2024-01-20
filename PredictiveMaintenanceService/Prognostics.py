# TODO: state transition
# TODO: report generation
class Prognostics:
    def __init__(self, report_callback):
        self.current_state = self.prognostic_state
        self.report_callback = report_callback

    def run(self, data):
        """
        executes the state state transition
        """
        self.current_state = self.current_state(data)
        while True:
            self.current_state = self.current_state(data)
            if self.current_state == self.idle_state_fault:
                break
        return self.current_state

    # def idle_state(self, data):
    #     if self.time_cycle_due():
    #         return self.prognostic_state
    #     return self.idle_state

    def prognostic_state(self, data):
        degradation_trend, trend_analysis_result = self.predict_degradation_trend(data)
        if trend_analysis_result:
            return lambda _: self.rul_predict_state(degradation_trend)
        else:
            return self.assessment_state

    def rul_predict_state(self, degradation_trend):
        rul = self.estimate_rul(degradation_trend)
        return lambda _: self.assessment_state(rul)

    def assessment_state(self, rul):
        health_status = self.analyze_health_status(rul)
        report = self.report_generate(health_status)
        self.report_send(report)
        return self.idle_state

    def predict_degradation_trend(self, data):
        degradation_trend = "test"
        trend_analysis_result = True
        return degradation_trend, trend_analysis_result

    def estimate_rul(self, degradation_trend):
        return 100

    def analyze_health_status(self, rul):
        return "Good"

    def report_generate(self, health_status):
        """
        Generate a report based on the prognostics information
        """
        return 0

    def report_send(self, report):
        """
        Send the report to the health management system.
        """
        if self.report_callback:
            self.report_callback(report)
