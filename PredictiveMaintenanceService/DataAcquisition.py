import pandas as pd
import logging


class DataAcquisition:
    def __init__(self):
        self.accumulated_data = pd.DataFrame()

    def access_data(self, sensor_data_generator):
        """
        Accesses data from the sensor data generator.
        """
        logging.info("Acquiring data...")
        try:
            data = pd.DataFrame(
                next(sensor_data_generator), index=[len(self.accumulated_data)]
            )
            self.accumulated_data = self.accumulated_data._append(
                data, ignore_index=True
            )
            return data
        except StopIteration:
            return None

    def get_data(self):
        """
        Gets all accumulated data
        """
        return self.accumulated_data
