from datetime import datetime
from typing import List
import logging
import pandas as pd
import queue
import random
import threading
import time

import random
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict
import requests
import pickle
import os
import logging

# Set up logging
logging.basicConfig(
    filename="maintenance_management.log",
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s",
)

from MaintenanceManagementService.monitoring import MonitoringUI


# TODO: Monitoring code integrate to new one
class Advisory:
    def __init__(self, condition, severity, timestamp, advisory):
        self.condition = condition
        self.severity = severity
        self.timestamp = timestamp
        self.advisory = advisory

    def get_details(self) -> str:
        return f"Condition: {self.condition}, Severity: {self.severity}, Time: {self.timestamp}"


class MaintenanceServiceSystem:
    def __init__(self):
        self.advisory = pd.DataFrame()  # Advisory()
        self.data_queue = queue.Queue()
        self.monitoring_ui = MonitoringUI(self.data_queue)

    def run(self):
        print("Succesfully running maintenance service system.")
        self.real_time_monitoring()

    def real_time_monitoring(self):
        threading.Thread(target=self.update_ui, daemon=True).start()
        self.monitoring_ui.run()

    def update_ui(self):
        while True:
            self.data_queue.put({"Metric1": 15, "Metric2": 10})
            time.sleep(0.1)
