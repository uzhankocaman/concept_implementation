from datetime import datetime
from typing import List
import logging
import pandas as pd
import queue
import random
import threading
import time 

from MaintenanceManagementService.monitoring import MonitoringUI

# TODO: use the information from the advisory to update update_maintenance_schedule
# TODO: inventory and logistics management
# TODO: alert notification 
class Advisory:
    def __init__(self, condition: str = ".", severity: str = ".", timestamp: datetime = datetime.datetime(1999, 8, 5), advisory: str = "."):
        self.condition = condition
        self.severity = severity
        self.timestamp = timestamp
        self.advisory = advisory

    def get_details(self) -> str:
        return f"Condition: {self.condition}, Severity: {self.severity}, Time: {self.timestamp}"

class MaintenanceServiceSystem:
    def __init__(self):
        self.advisory = pd.DataFrame() # Advisory()
        self.data_queue = queue.Queue()
        self.monitoring_ui = MonitoringUI(self.data_queue)
        
    def run(self):
        print("Succesfully running maintenance service system.")
        # self.real_time_monitoring()

    def real_time_monitoring(self):
        threading.Thread(target=self.update_ui, daemon=True).start()
        self.monitoring_ui.run()
        
    def update_ui(self):
        while True:
            self.data_queue.put({
                'Metric1': 15,
                'Metric2': 10
            })
            time.sleep(0.1)
            
    def receive_advisory(self, report):
        """
        Receives and stores advisory.
        """
        logging.info("Advisory received.")
        self.advisory = self.advisory._append(report)

    def update_maintenance_schedule(self, advisories: List[Advisory]):
        pass

    def manage_inventory(self, advisories: List[Advisory]):
        pass

    def manage_logistics(self, advisories: List[Advisory]):
        pass

    def send_alert_notifications(self):
        print("Sending alert notifications.")
