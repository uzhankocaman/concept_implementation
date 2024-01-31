import pandas as pd
import logging
from datetime import datetime
from utilities.observer_pattern import Event, Observer


class DataAcquisition:
    def __init__(self):
        self.accumulated_data = None
        self.on_data_accessed = Event()
        # The rest can also be initialized here, for DA becoming the single connection between PMS and DTM.
        # self.data_processor = DataProcessing()
        # self.state_adaptation = StateAdaptation()
        # self.fault_diagnostic = FaultDiagnostic()
        # self.prognostic = Prognostics()
        # self.health_management = HealthManagement()
        # self.maintenance_management = MaintenanceManagementService()
        # self.data_provider = DataProviderService()

        # # Subscribe
        # self.data_acquisition.on_data_accessed.subscribe(self.data_processor)
        # self.data_processor.on_data_processed.subscribe(self.state_adaptation)
        # self.state_adaptation.on_state_assessed.subscribe(self.fault_diagnostic)
        # self.state_adaptation.on_state_assessed.subscribe(self.prognostic)
        # self.fault_diagnostic.fault_state_assessed.subscribe(self.health_management)
        # self.prognostic.prognostic_state_assessed.subscribe(self.health_management)
        # self.health_management.health_management_complete.subscribe(self.maintenance_management)

    def collect_data(self, entry, data_type):
        self.entry = entry
        df = pd.Series(
            {
                "timestamp": self.entry.features["ml40::Time"].time,
                "Bat_Volt": self.entry.features["ml40::Composite"]
                .targets["Battery"]
                .features["ml40::BatteryStatus"]
                .voltage,
                "FuelPressure": self.entry.features["ml40::Composite"]
                .targets["Fuel Filter"]
                .features["ml40::Pressure"]
                .pressure,
                "RPM_Diesel": self.entry.features["ml40::Composite"]
                .targets["Diesel Engine"]
                .features["ml40::RotationalSpeed"]
                .rpm,
            }
        )
        df["data_type"] = data_type  # filter, battery
        df["datetime"] = datetime.fromtimestamp(int(df["timestamp"]))
        self.on_data_accessed.emit(df.copy())

    def store_data(self, df):
        if self.accumulated_data is None:
            self.accumulated_data = df
        else:
            self.accumulated_data = self.accumulated_data.append(df, ignore_index=True)
