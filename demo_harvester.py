from ml import build, setup_logger, S3IConnector, Thing, S3IParameter, APP_LOGGER
from ml.ml40.features.functionalities.provides_machine_data import ProvidesMachineData
from ml.ml40.features.functionalities.predicts_maintenance import PredictsMaintenance
from ml.ml40.features.functionalities.manages_maintenance import ManagesMaintenance
import asyncio
import argparse
import yaml
from DataProviderService.dps import DataProviderService
from PredictiveMaintenanceService.observer_pattern import Event, Observer
# from MaintenanceManagementService.MaintenanceManagementSystem import (
#     MaintenanceManagementService,
# )

# self.entry.features["ml40::Composite"].targets["Diesel Engine"].features["ml40::Composite"].targets["Fuel"].features["ml40::Pressure"].pressure
# self.entry.features["ml40::ProvidesMachineData"]
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
        {"class": "fml40::ProvidesMachineData"},
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
                        "class": "ml40::Composite",
                        "targets": 
                        [
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
                                        "class": "ml40::PressureSensor"
                                    },
                                ],
                                "features": 
                                [
                                    {
                                        "class": "ml40::BatteryStatus",
                                        "voltage": 0,
                                        "maintenanceSchedule": 0,
                                        "lastMaintenanceDate": 0,
                                        "test": 0,
                                    },
                                ]
                            },
                        ]
                    },
                    {
                        "class": "ml40::RotationalSpeed",
                        "rpm": 0
                    },
                    {
                        "class": "ml40::Temperature",
                        "temperature": 0
                    },
                    {
                        "class": "ml40::CurrentLoad",
                        "load": 0
                    },
                    {
                        "class": "ml40::MachineOperatingStatus",
                        "status": "defekt"
                    },
                ]
            },
            ]
        },
        {
        "class": "ml40::ProvidesMachineData",
        },
        {
        "class": "ml40::OperatingHours",
        "total": 0
        },
    ]
  }
}

class DemoHarvester(Thing):
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
        setup_logger("Demo Harvester")
        super(DemoHarvester, self).__init__(loop=loop, entry=entry, connector=connector)

    berechne_pm()
    speichern

    def simulate_operating_hours(self):
        
         
        
        self.loop.call_later(10, self.simulate_operating_hours)

    def simulate_operating_hours(self):
        """
        Recursively increases operating hours every 10 seconds.

        """
        operating_hours = self.entry.features["ml40::OperatingHours"]
        operating_hours.total += 0.1
        APP_LOGGER.info("Current value: {}".format(operating_hours.total))
        # print(result)
        # mms = MaintenanceManagementService()
        # mms.run()
        self.loop.call_later(10, self.simulate_operating_hours)

    def recursively_send_named_event(self):
        """
        Recursively sends named event (update of ml40::OperationHours) every 10 seconds.
        """
        current_operating_hours = self.entry.features["ml40::OperatingHours"].total

        current_operating_hours = {
            "currentOperatingHours": round(current_operating_hours, 1)
        }
        self.connector.add_broker_event_message_to_send(
            "{}.newOperatingHours".format(self.entry.identifier),
            current_operating_hours,
        )
        self.loop.call_later(10, self.recursively_send_named_event)

    def run(self):
        """
        Defines the run function, adds callback functions and start the event loop in a persistent module.
        """
        # self.add_ml40_implementation(
        #     DataProviderService, "ml40::ProvidesMachineData"
        # )
        self.add_on_thing_start_ok_callback(self.simulate_operating_hours, True, False)
        self.connector.add_on_event_system_start_ok_callback(
            self.recursively_send_named_event, True, False
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
    har = DemoHarvester(
        oauth2_id=oauth2_id,
        oauth2_secret=oauth2_secret,
    )
    har.run()

# DataProviderService()