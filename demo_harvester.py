from ml import build, setup_logger, S3IConnector, Thing, S3IParameter, APP_LOGGER
from ml.fml40.features.functionalities.accepts_felling_jobs import AcceptsFellingJobs
import asyncio
import argparse

# from MaintenanceManagementService.MaintenanceManagementSystem import (
#     MaintenanceManagementService,
# )

# self.entry.features["ml40::Composite"].targets["Diesel Engine"].features["ml40::Composite"].targets["Fuel"].features["ml40::Pressure"].pressure
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
                        "class": "ml40::Composite",
                        "targets": 
                        [
                            {
                                "class": "ml40:Thing",
                                "name": "Fuel",
                                "roles": 
                                [
                                    {
                                        "class": "ml40::PressureSensor"
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
                                        "class": "ml40::Pressure",
                                        "voltage": 0
                                    },
                                ]
                            },
                            # {
                            #     "class": "ml40::Thing",
                            #     "name": "Battery",
                            #     "roles": 
                            #     [
                            #         {
                            #             "class": "fml40::Battery"
                            #         },
                            #     ],
                            #     "features": 
                            #     [
                            #         {
                            #         "class": "fml40::Battery",
                            #         # "voltage": 0,
                            #         # "maintenanceSchedule": "",
                            #         # "lastMaintenanceDate": ""
                            #         }
                            #     ]
                            # },
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
                        "status": ""
                    },
                ]
            },
            ]
        },
        {
        "class": "ml40::ProvidesMachineData",
        "Bat_Volt": 0,
        "Oil_Temp":	0,
        "Cool_Temp": 0,	
        "FuelPressure": 0,	
        "Engine_Load": 0,
        "RPM_Diesel": 0
        },
        {
        "class": "ml40::OperatingHours",
        "total": 0
        },
    ]
  }
}


# # Other
# {
#     "class": "ml40::ProvidesMachineData",
# },
# {
#     "class": "ml40::OperatingHours",
#     "total": 0
# },

# # Engine
# {
#     "class": "ml40::Thing",
#     "name": "Diesel Engine",
#     "roles": [
#         {
#             "class": "ml40::Engine"
#         }
#     ],
#     "features": [
#         {
#             "class": "ml40::RotationalSpeed",
#             "rpm": 0
#         },
#         {
#             "class": "ml40::Temperature",
#             "temperature": 0
#         },
#         {
#             "class": "ml40::EngineLoad",
#             "load": 0
#         },
#         {
#             "class": "ml40::Battery",
#             "voltage": 0,
#             "maintenanceSchedule": "",
#             "lastMaintenanceDate": ""
#         },
#         {
#         "class": "ml40:Thing",
#         "name": "Fuel",
#         "roles": [
#             {
#                 "class": "ml40::PressureSensor"
#             }
#         ],
#         "features": [
#             {
#                 "class": "ml40::Pressure",
#                 "pressure": 0
#             }
#         ]
#         },
#         {
#             "class": "ml40::MachineOperatingStatus",
#             "status": ""
#         },
#     ]
# }

# {
#             "class": "ml40::FuelFilter",
#             "fuelPressure": 0,
#             "maintenanceSchedule": "",
#             "lastMaintenanceDate": ""
        #   },


# {
#             "class": "ml40::Pressure",
#             "pressure": 0
#           },
###
###
# {
#     "class": "ml40::FuelConsumption",
#     "currentConsumption": 0,
#     "meanConsumption": 0
# },
# ###
# {
# "class": "ml40::PredictsMaintenance",
# },
# {
# "class": "ml40::MaintenanceManagementService",
# },
# {
# "class": "ml40::DataProviderService",
# },

# {
#             "class": "ml40::FuelFilter",
#             "fuelPressure": 0,
#             "maintenanceSchedule": "",
#             "lastMaintenanceDate": ""
# },

# Implementation object is added into the functionality fml40::AcceptsFellingJobs
class AcceptsFellingJobsImpl(AcceptsFellingJobs):
    """
    Reference implements a fml40 feature (fml40::AcceptsFellingJob)
    """

    def __init__(self, name="", identifier=""):
        super(AcceptsFellingJobs, self).__init__(name=name, identifier=identifier)

    async def acceptJob(self, job):
        """
        Implementation logic for how to accept a felling job

        :param job: concrete felling order
        :return: bool
        """
        print("Receive a felling job which is {}".format(job))
        return True


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

    def simulate_operating_hours(self):
        """
        Recursively increases operating hours every 10 seconds.

        """
        operating_hours = self.entry.features["ml40::OperatingHours"]
        operating_hours.total += 0.1
        APP_LOGGER.info("Current value: {}".format(operating_hours.total))
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
        print("run")
        self.add_ml40_implementation(
            AcceptsFellingJobsImpl, "fml40::AcceptsFellingJobs"
        )
        self.add_on_thing_start_ok_callback(self.simulate_operating_hours, True, False)

        self.connector.add_on_event_system_start_ok_callback(
            self.recursively_send_named_event, True, False
        )

        self.run_forever()


if __name__ == "__main__":
    # parser = argparse.ArgumentParser()
    # parser.add_argument("-i", "--oauth2_id", type=str, help="OAuth2 Identifier of DT Harvester", required=True)
    # parser.add_argument('-s', '--oauth2_secret', type=str, help='OAuth2 Secret of DT Harvester', required=True)
    # args = parser.parse_args()
    # har = DemoHarvester(oauth2_id=args.oauth2_id, oauth2_secret=args.oauth2_secret)
    har = DemoHarvester(
        oauth2_id="s3i:c2c713c4-910f-405f-86af-e2ce67f6bea5",
        oauth2_secret="Jb7dmOzHF8zuokZMzC9cG2KiHgZJEGJK",
    )
    har.run()
