import pandas as pd
import logging


class HealthManagement:
    def __init__(self, report_callback):
        self.reports = pd.DataFrame()
        self.report_callback = report_callback

    def receive_report(self, report):
        """
        Receives and stores reports.
        """
        logging.info("Report received.")
        self.reports = self.reports._append(report)

    def process_reports(self):
        """
        Process all received reports. Integrate information from the reports.
        """
        logging.info("Processing reports.")

        if not self.reports.empty:
            self.__generate_advisory()
            self.__send_advisory()
            self.reports = pd.DataFrame()  # Clear the list after processing
        else:
            print("No reports to process.")

    def __generate_advisory(self):
        self.reports["Advisory"] = "Change Battery"

    def __send_advisory(self):
        self.report_callback(self.reports)
