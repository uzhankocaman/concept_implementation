class HealthManagement:
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