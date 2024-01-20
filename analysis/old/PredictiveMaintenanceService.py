import pandas as pd
import numpy as np
import time

transmission_interval = 0


# SENSOR BEHAVIOR SIMULATION
def simulated_sensor(file_path):
    data = pd.read_excel(file_path)
    data_records = data.to_dict("records")
    for record in data_records:
        yield record
        time.sleep(transmission_interval)


# DATA ACQUISITION
def access_data(simulated_sensor_generator):
    try:
        return next(simulated_sensor_generator)
    except StopIteration:
        return None


def store_data(accumulated_data: pd.DataFrame, data_row: pd.Series):
    return accumulated_data._append(data_row, ignore_index=True)


def data_acquisition(sensor_data_generator):
    data_row = access_data(sensor_data_generator)
    return data_row, data_row is not None


# DATA PROCESSING
def process_data(raw_data):
    """
    Code for data preprocessing: scaling
    """
    clean_data = cleaning_data(raw_data)
    # ...
    feature_data = feature_engineering(clean_data)
    return feature_data


def cleaning_data(raw_data):
    # missing value, duplicates, data type conversion, typo, unnecessary columns
    cleaned_data = raw_data.dropna(axis=1, how="all")
    for i in range(1, 82):
        try:
            cleaned_data = cleaned_data.drop([f"Unnamed: {i}"], axis=1)
        except KeyError:
            continue
    cleaned_data.rename(columns={"Unnamed: 0": "Time"}, inplace=True)
    ref = cleaned_data["Time"][0]
    cleaned_data = cleaned_data.iloc[0:969]
    cleaned_data["ReferenceTime"] = cleaned_data.apply(
        lambda x: (x["Time"] - ref).total_seconds(), axis=1
    )
    col = cleaned_data.pop("ReferenceTime")
    cleaned_data.insert(1, col.name, col)
    return cleaned_data


# FEATURE ENGINEERING
def feature_engineering(clean_data):
    # elapsed time since last maintenance
    # rolling mean
    window_size = 2
    # threshold with interpolation
    # fuel efficiency
    feature_data = elapsed_time(clean_data)
    feature_data = rolling_mean(feature_data, "DieselData.Fuelconsumption", window_size)
    feature_data = rolling_std(feature_data, "DieselData.Speed", window_size)
    feature_data = change_in_sensor_readings(feature_data, "DieselData.Fuelconsumption")
    feature_data = fuel_efficiency(
        feature_data, "DieselData.Fuelconsumption", "DieselData.OperatHours"
    )
    feature_data = cumulative_operating_hours(feature_data, "DieselData.OperatHours")
    feature_data = state_transitions(feature_data, "MaschineStatus.WorkHydraulikAktiv")
    feature_data = pressure_difference(
        feature_data, "Pumpe_Ibc_Obc_Druck.IbcP", "Pumpe_Ibc_Obc_Druck.ObcP"
    )

    return feature_data


# Functions for each feature
def elapsed_time(df):
    df["Elapsed_Time_Feature"] = (df["Time"] - df["Time"].min()).dt.total_seconds()
    return df


def rolling_mean(df, column_name, window_size):
    df[f"{column_name}_Rolling_Mean_Feature"] = (
        df[column_name].rolling(window=window_size).mean()
    )
    return df


def rolling_std(df, column_name, window_size):
    df[f"{column_name}_Rolling_Std_Feature"] = (
        df[column_name].rolling(window=window_size).std()
    )
    return df


def change_in_sensor_readings(df, column_name):
    df[f"{column_name}_Change_Feature"] = df[column_name].diff()
    return df


def fuel_efficiency(df, fuel_col, hours_col):
    df["Fuel_Efficiency_Feature"] = df[fuel_col] / df[hours_col]
    return df


def cumulative_operating_hours(df, column_name):
    df[f"{column_name}_Cumulative_Feature"] = df[column_name].cumsum()
    return df


def state_transitions(df, column_name):
    df[f"{column_name}_State_Changes_Feature"] = df[column_name].diff().abs()
    return df


def pressure_difference(df, pressure1, pressure2):
    df["Pressure_Difference_Feature"] = df[pressure1] - df[pressure2]
    return df


# FAULT DIAGNOSTICS
def fault_diagnostics_system():
    current_state = idle_state_fault  # Initial state

    def transition(data):
        nonlocal current_state
        while True:
            current_state = current_state(data)
            if current_state is idle_state_fault:
                return 0  # or break?

    return transition


def idle_state_fault(data):
    """
    detects incoming events
    """
    if event_detected(data):  # if there is incoming data
        return diagnostic_state
    return idle_state_fault


def diagnostic_state(data):
    """
    detects the fault
    """
    if fault_detection(data):  # if there is a fault detected
        return fault_processing_state
    return idle_state_fault


def fault_processing_state(data):
    """
    processes the fault, by determining time, location and severity of fault
    """
    fault_time = alarm(data)
    fault_location = fault_isolation(data)
    fault_severity = fault_identification(data)
    return lambda _: assessment_state_fault(fault_time, fault_location, fault_severity)


def assessment_state_fault(fault_time, fault_location, fault_severity):
    """
    creates a report of fault to send to health management
    """
    report = report_generate(fault_time, fault_location, fault_severity)
    report_send(report)
    return idle_state_fault


def event_detected(data):
    """
    check if data is available
    """
    return data is not None


def fault_detection(data):
    """
    check if data exceeds/deceeds certain threshold
    """
    return data["MaschineStatus.DieselFuellstand"] < 9999


def alarm(data):
    # alarm/notification
    print("Fault detected!")
    return {"fault_time": "11/13/2023 17:39"}


def fault_isolation(data):
    return {"fault_location": "Diesel Fuellstand"}


def fault_identification(data):
    return {"fault_severity": "Level 4/5"}


def report_generate(fault_time, fault_location, fault_severity):
    """
    Generate a report based on the fault information
    """
    return pd.DataFrame.from_dict(
        fault_time | fault_location | fault_severity, orient="index"
    )


def report_send(report):
    """
    Send the report to the health management system.
    """
    health_management.receive_report(report)


# PROGNOSTICS ASSESSMENT
def prognostics_assessment():
    current_state = idle_state_prognostics  # Initial state

    def transition(data):
        nonlocal current_state
        current_state = current_state(data)
        return current_state

    return transition


def idle_state_prognostics(data):
    if time_cycle_due():
        return prognostic_state
    return idle_state_prognostics


def prognostic_state(data):
    # Run prognostic procedure to predict degradation trends
    degradation_trend, trend_analysis_result = predict_degradation_trend(data)

    # Determine whether to proceed based on the trend analysis
    if trend_analysis_result:  # Replace with actual condition check
        # Transition to rul_predict_state with the trend information
        return lambda _: rul_predict_state(degradation_trend)
    else:
        # If the degradation trend does not indicate a need for RUL prediction,
        # return to the idle state and wait for the next cycle
        return idle_state_prognostics


def rul_predict_state(degradation_trend):
    # Estimate RUL based on the degradation trend
    rul = estimate_rul(degradation_trend)
    # After estimating the RUL, proceed to the assessment state
    return lambda _: assessment_state_prognostics(rul)


def assessment_state_prognostics(rul):
    # Analyze health status and forward the report to health management
    health_status = analyze_health_status(rul)
    report = generate_health_report(health_status)
    send_health_report(report)
    # After sending the report, transition back to idle_state
    return idle_state_prognostics


def time_cycle_due():
    return True


def predict_degradation_trend(data):
    # Perform analysis to determine the degradation trend
    degradation_trend = "test"
    trend_analysis_result = True
    return degradation_trend, trend_analysis_result


def estimate_rul(degradation_trend):
    # RUL estimation logic
    rul = 100


def analyze_health_status(rul):
    # health status analysis logic
    health_status = "Good"
    return health_status


def generate_health_report(health_status):
    report = "Health Report"
    return report


def send_health_report(report):
    # report sending logic to health management
    print("Sending report:", report)


# HEALTH MANAGEMENT
def health_management():
    # Wait for assessment reports
    reports = receive_reports()
    # Reports are received, analyze them and generate maintenance advisories
    advisories = generate_advisories(reports)
    # Transmit the advisories to the external system for maintenance decision-making
    transmit_advisories(advisories)


class HealthManagementSystem:
    def __init__(self):
        self.reports = []

    def receive_report(self, report):
        """
        Receives and stores reports.
        """
        self.reports.append(report)
        print("Report received and stored.")

    def process_reports(self):
        """
        Process all received reports.
        """
        if self.reports:
            print("Processing reports in health management system:")
            for report in self.reports:
                print(report)
            # Clear the list after processing
            self.reports.clear()
        else:
            print("No reports to process.")

    def generate_advisory(self, reports):
        pass


def receive_reports():
    return ["report1", "report2"]


def generate_advisories(reports):
    return ["advisory1", "advisory2"]


def transmit_advisories(advisories):
    for advisory in advisories:
        print("Transmitting advisory:", advisory)


# MAIN
def main():
    health_management = HealthManagementSystem()

    file_path = "CAN_short_20220504_cleaned.xlsx"
    sensor_data_generator = simulated_sensor(file_path)
    stored_data = pd.DataFrame()

    # Loop to simulate continuous data acquisition
    while True:
        raw_data, data_available = data_acquisition(sensor_data_generator)
        if not data_available:
            break
        else:
            stored_data = store_data(stored_data, raw_data)
        processed_data = process_data(stored_data)  # change to row-wise processing?

    print("entering fault_diagnostic_assessment")
    for index, processed_datapoint in processed_data.iterrows():
        # # FAULT DIAGNOSTICS
        fault_diagnostic_assessment = fault_diagnostics_system()
        fault_diagnostic_assessment(processed_datapoint)


# # PROGNOSTICS ASSESSMENT
# state_machine = prognostics_assessment()
# transition_function = state_machine(data)
# if callable(transition_function):
#     # If the state returns a callable, it's a lambda, so call it to get the next state
#     state_machine = transition_function

# # HEALTH MANAGEMENT
# health_management_report = health_management(fault_diagnostics_report, prognostics_report)
# transmit(health_management_report)
