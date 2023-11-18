import pandas as pd

class DataAcquisition:
    def __init__(self):
        self.accumulated_data = pd.DataFrame()

    def access_data(self, sensor_data_generator):
        """
        Accesses data from the sensor data generator.
        """
        try:
            return next(sensor_data_generator)
        except StopIteration:
            return None

    def set_data(self, data_row):
        """
        Sets a row of data in the accumulated DataFrame.
        """
        if data_row is not None:
            self.accumulated_data = self.accumulated_data.append(data_row, ignore_index=True)

    def get_data(self):
        """
        Gets all accumulated data
        """
        return self.accumulated_data

# Example usage
# Assuming the existence of a sensor data generator function
sensor_data_generator = simulated_sensor("sensor_data.xlsx")  # Replace with the actual generator
data_acquisition_system = DataAcquisition()

# Acquire and store a single data row
data_row, data_available = data_acquisition_system.acquire_data(sensor_data_generator)
