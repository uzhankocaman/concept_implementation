from ml import build, setup_logger, S3IConnector, Thing, S3IParameter, APP_LOGGER
import asyncio
import argparse
import yaml
import pandas as pd

from PredictiveMaintenanceService.DataAcquisition import DataAcquisition
from PredictiveMaintenanceService.DataProcessing import DataProcessing
from PredictiveMaintenanceService.StateAdaptation import StateAdaptation
from PredictiveMaintenanceService.Prognostics import Prognostics
from PredictiveMaintenanceService.FaultDiagnostics import FaultDiagnostic
from PredictiveMaintenanceService.HealthManagement import HealthManagement
from MaintenanceManagementService.MaintenanceManagementSystem import MaintenanceManagementService
from DataProviderService.dps import DataProviderService

from utilities.observer_pattern import Event, Observer
"""
Serializes the DT modeling conform to ForestML 4.0.
"""

harvester_fml40_json = {
  "thingId": "",
  "policyId": "",
  "attributes": {
    "class": "ml40::Thing",
    "name": "Maintenance Analysis Harvester",
    "roles": [
      {
        "class": "fml40::Harvester"
      }
    ],
    "features": 
    [
        {
        "class": "ml40::Composite",
        "targets": [
            {
                "class": "ml40::Thing",
                "name": "Diesel Engine",
                "roles": [
                    {
                        "class": "ml40::Engine"
                    }
                ],
                "features": 
                [
                    {
                        "class": "ml40::RotationalSpeed",
                        "rpm": 0
                    },
                    # {
                    #     "class": "ml40::CurrentLoad",
                    #     "load": 0
                    # },
                ]
            },
            {
                "class": "ml40:Thing",
                "name": "Fuel Filter",
                "roles": 
                [
                    {
                        "class": "ml40::FuelFilter" #FuelFilter
                    },
                ],
                "features": 
                [
                    {
                        "class": "ml40::Pressure",
                        "pressure": 0
                    },
                ]
            },
            {
                "class": "ml40:Thing",
                "name": "Battery",
                "roles": 
                [
                    {
                        "class": "fml40::Battery"
                    },
                ],
                "features": 
                [
                    {
                        "class": "ml40::BatteryStatus",
                        "voltage": 0,
                    },
                ]
            },
            ]
        },
        {
        "class": "ml40::Time",
        "time": 0
        },
    ]
  }
}

# {
#     "class": "ml40::Thing",
#     "name": "",
#     "roles": [
#         {
#             "class": "ml40::TemperatureSensor"
#         }
#     ],
#     "features": [
#         {
#             "class": "ml40::Temperature",
#             "temperature": 50
#         }
#     ]
# },

class MaintenanceAnalysisHarvester(Thing):
    """
    Defines demo harvester
    """

    def __init__(self, oauth2_id, oauth2_secret):
        """
        Initializes demo havester
        """

        model = harvester_fml40_json

        """
        Fills the thingId and policyId with oauth2 id 
        """
        model["thingId"] = oauth2_id
        model["policyId"] = oauth2_id
        # model["attributes"]["features"].append(
        #         {
        #             "class": "ml40::EventList",
        #             "subFeatures": [
        #                 {
        #                     "class": "ml40::Event",
        #                     "topic": "{}.newMaintenanceInformation".format(oauth2_id),
        #                     "description": "",
        #                     "frequency": 1,
        #                     "schema": {},
        #                     "exampleContent":  {
        #                         "reports": {
        #                             0: {
        #                                     "Maintenance Report Type": "",
        #                                     "Analysis": {
        #                                         "Operational Condition": "",
        #                                         "Health Status": "",
        #                                         "Fault Location": "",
        #                                         "Time Detected": "",
        #                                         "Fault Severity (1-5 scale)": "",
        #                                         "Analysis": "",
        #                                         "Maintenance Required": ""
        #                                     }
        #                                 },
        #                             1: {
        #                                     "Maintenance Report Type": "",
        #                                     "Analysis": {
        #                                         "Operational Condition": "",
        #                                         "Health Status": "",
        #                                         "Fault Location": "",
        #                                         "Time Detected": "",
        #                                         "Fault Severity (1-5 scale)": "",
        #                                         "Analysis": "",
        #                                         "Maintenance Required": ""
        #                                     }
        #                             }
        #                         }
        #                     }
        #                 }
        #             ]
        #         }
        #     )
        model["attributes"]["features"].append(
                {
                    "class": "ml40::EventList",
                    "subFeatures": [
                        {
                            "class": "ml40::Event",
                            "topic": "{}.newMaintenanceInformation".format(oauth2_id),
                            "description": "",
                            "frequency": 1,
                            "schema": {},
                            "exampleContent":  {
                                "reports": 111
                            }
                        }
                    ]
                }
            )


        """
        Gets the running event loop 
        """
        loop = asyncio.get_event_loop()

        """
        Instantiates an entry class
        """
        entry = build(model)

        """
        Specifies the used parameter for S3I connection
        """
        parameter = S3IParameter(repo_sync_freq=0.01)

        """
        Instantiates an connector class 
        """
        connector = S3IConnector(
            oauth2_id=oauth2_id,
            oauth2_secret=oauth2_secret,
            is_repository=True,
            is_broker_rest=False,
            is_broker=True,
            dt_entry_ins=entry,
            loop=loop,
            s3i_parameter=parameter,
        )
        setup_logger("Maintenance Analysis Harvester")
        super(MaintenanceAnalysisHarvester, self).__init__(loop=loop, entry=entry, connector=connector)
        self.data_acquisition = DataAcquisition()
        # The rest can also be initialized within DataAcquisition(), for DA becoming the single connection between PMS and DTM.
        self.data_processor = DataProcessing()
        self.state_adaptation = StateAdaptation()
        self.fault_diagnostic = FaultDiagnostic()
        self.prognostic = Prognostics()
        self.health_management = HealthManagement()
        self.maintenance_management = MaintenanceManagementService()
        self.data_provider = DataProviderService()

        # Subscribe
        self.data_acquisition.on_data_accessed.subscribe(self.data_processor)
        self.data_processor.on_data_processed.subscribe(self.state_adaptation)
        self.state_adaptation.on_state_assessed.subscribe(self.fault_diagnostic)
        self.state_adaptation.on_state_assessed.subscribe(self.prognostic)
        self.fault_diagnostic.fault_state_assessed.subscribe(self.health_management)
        self.prognostic.prognostic_state_assessed.subscribe(self.health_management)
        self.health_management.health_management_complete.subscribe(self.maintenance_management)

    def service_call(self):
        # dps   
        # self.entry.features["ml40::Time"].time = 1700747727
        # self.entry.features["ml40::Composite"].targets["Battery"].features["ml40::BatteryStatus"].voltage = 278
        # self.entry.features["ml40::Composite"].targets["Fuel Filter"].features["ml40::Pressure"].pressure = 4.44
        # self.entry.features["ml40::Composite"].targets["Diesel Engine"].features["ml40::RotationalSpeed"].rpm = 799
        self.entry.features["ml40::Time"].time, self.entry.features["ml40::Composite"].targets["Diesel Engine"].features["ml40::RotationalSpeed"].rpm, self.entry.features["ml40::Composite"].targets["Fuel Filter"].features["ml40::Pressure"].pressure, self.entry.features["ml40::Composite"].targets["Battery"].features["ml40::BatteryStatus"].voltage = self.data_provider.getMachineData()
        # pm
        self.data_acquisition.collect_data(self.entry, 'battery')
        self.data_acquisition.collect_data(self.entry, 'filter')
        self.entry.features["ml40::EventList"].subFeatures["ml40::Event"].exampleContent["reports"] = self.maintenance_management.get_reports()
        print(self.entry.features["ml40::EventList"].subFeatures["ml40::Event"].exampleContent["reports"])
        # self.data_provider.information_gateway.store_db(reports)
        # print("Hello")
        # mms
        # speichern dps call
        self.loop.call_later(10, self.service_call)

    # def simulate_operating_hours(self):
    #     """
    #     Recursively increases operating hours every 10 seconds.

    #     """
    #     print("Start Variables")
    #     print(self.entry.features["ml40::Composite"].targets["Diesel Engine"].features["ml40::RotationalSpeed"].rpm)
    #     print(self.entry.features["ml40::Time"].time)
    #     print(self.entry.features["ml40::Composite"].targets["Fuel Filter"].features["ml40::Pressure"].pressure)
    #     print(self.entry.features["ml40::Composite"].targets["Battery"].features["ml40::BatteryStatus"].voltage)
    #     print("End Variables")
    #     operating_hours = self.entry.features["ml40::Time"]
    #     operating_hours.time += 0.1
    #     APP_LOGGER.info("Current value: {}".format(operating_hours.time))
    #     # print(result)
    #     # mms = MaintenanceManagementService()
    #     # mms.run()
    #     self.loop.call_later(10, self.simulate_operating_hours)

    def send_event_maintenance_information(self):
        # msg = self.entry.features["ml40::EventList"].subFeatures["ml40::Event"].exampleContent
        msg = {"reports": 999}
        self.connector.add_broker_event_message_to_send(
            "{}.{}".format(self.entry.identifier, "newMaintenanceInformation"), msg)
        self.loop.call_later(10, self.send_event_maintenance_information)

    def run(self):
        """
        Defines the run function, adds callback functions and start the event loop in a persistent module.
        """
        # self.add_ml40_implementation(
        #     DataProviderService, "ml40::ProvidesMachineData"
        # )
        self.add_on_thing_start_ok_callback(self.service_call, True, False)
        self.connector.add_on_event_system_start_ok_callback(
            self.send_event_maintenance_information, True, False
        )
        self.run_forever()

def read_credentials_from_yaml(file_path):
    with open('credentials.yaml', 'r') as file:
        credentials = yaml.safe_load(file)
        return credentials
    
if __name__ == "__main__":
    # parser = argparse.ArgumentParser()
    # parser.add_argument("-i", "--oauth2_id", type=str, help="OAuth2 Identifier of DT Harvester", required=True)
    # parser.add_argument('-s', '--oauth2_secret', type=str, help='OAuth2 Secret of DT Harvester', required=True)
    # args = parser.parse_args()
    # har = DemoHarvester(oauth2_id=args.oauth2_id, oauth2_secret=args.oauth2_secret)
    credentials = read_credentials_from_yaml('credentials.yaml')
    oauth2_id = credentials['oauth2_id']
    oauth2_secret = credentials['oauth2_secret']    
    har = MaintenanceAnalysisHarvester(
        oauth2_id=oauth2_id,
        oauth2_secret=oauth2_secret,
    )
    har.run()

# DataProviderService()