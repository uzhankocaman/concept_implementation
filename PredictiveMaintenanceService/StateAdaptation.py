import pandas as pd
from utilities.observer_pattern import Event, Observer
import yaml

class StateAdaptation(Observer):
    def __init__(self):
        super().__init__()
        self.configuration_setting = None
        self.threshold_parameters = {}  # Adaptive threshold parameters
        self.processed_data = pd.Series()
        self.category = None
        self.operational_condition = None
        self.model = None
        self.value = None
        self.on_state_assessed = Event()
        self.known_conditions = {
            "battery": {},
            "filter": {},
        }
        self.load_known_conditions()

    def handle_event(self, processed_data):
        print("hello SAA event")
        self.processed_data = processed_data
        self.run()
        state_assessed_data = self.processed_data.copy()
        self.on_state_assessed.emit(state_assessed_data)
        self.processed_data = pd.Series()
        state_assessed_data = pd.Series()


    def load_known_conditions(self):
        with open('C://Users/U/Documents/4.Semester/Masterarbeit/concept_implementation/PredictiveMaintenanceService/known_conditions.yaml', 'r') as file:
            conditions = yaml.safe_load(file)
        for condition, expression in conditions['battery'].items():
            self.known_conditions['battery'][condition] = eval(f"lambda x: {expression}")
        for condition, expression in conditions['filter'].items():
            self.known_conditions['filter'][condition] = expression

    def run(self):
        # Start with aligning sensor data with machine configuration
        self.align_data_with_configuration()

        self.tune_model_based_on_optimization_criteria()

        self.link_data_to_operational_condition()    
        # Check if the operational condition is known
        if self.is_condition_known():
            # Set configuration to the corresponding known condition
            self.set_configuration_setting()
        else:
            # Adjust operating condition boundaries for new condition
            self.adjust_operating_condition_boundaries(self.processed_data)
            self.link_data_to_operational_condition()
            if self.is_condition_known(self.processed_data):
                self.set_configuration_setting()
            else:
                # Initialize a new configuration setting
                self.initialize_new_configuration_setting(self.processed_data)

    def link_data_to_operational_condition(self):
        self.operational_condition = None # Unknown condition
        if self.category == "battery":
            for condition_name, condition_func in self.known_conditions[self.category].items():
                if condition_func(self.processed_data[self.value]):
                    self.operational_condition = condition_name
        if self.category == "filter":
            self.operational_condition = self.known_conditions["filter"]["slope"] * self.processed_data["RPM_Diesel"] + self.known_conditions["filter"]["intercept"] 


    def set_configuration_setting(self):
        # Logic to set configuration based on known condition
        print(f"Setting configuration for condition: {self.operational_condition}")
        self.configuration_setting = {"data_type": self.category, "operational_condition": self.operational_condition, "model": self.model}
        self.processed_data["configuration"] = self.configuration_setting

    def align_data_with_configuration(self):
        # Based on the incoming data, determine which configuration steps to be taken
        dict = {"battery": "scale_value_Bat_Volt", "filter": "FuelPressure"}
        self.category = self.processed_data["data_type"]
        self.value = dict[self.category]

    def is_condition_known(self):
        # Check if the operational condition is known within the specified category
        if self.category == "battery":
            category_conditions = self.known_conditions.get(self.category)
            if category_conditions and self.operational_condition in category_conditions:
                return True
        if self.category == "filter" and self.operational_condition != None:
            return True
        return False

    def initialize_new_configuration_setting(self, data):
        self.set_configuration_setting() # deployed with nan

    def adjust_operating_condition_boundaries(self, data):
        # Current version supporting battery only as it has discrete boundaries
        if self.category == 'battery':
            # Threshold optimization
            max_extension = 5  # Maximum allowable extension for a condition boundary
            closest_condition = None
            closest_distance = float('inf')  # Initialize with a large number

            # Find the closest condition that can be extended
            for condition, check in self.known_conditions[self.category].items():
                if isinstance(check, tuple):  # Check if condition is a range
                    lower, upper = check

                    # Calculate distance to the closest boundary of the condition
                    distance = min(abs(lower - data), abs(upper - data))

                    # Check if this condition is closer and can be extended to include new data
                    if distance < closest_distance and (lower - max_extension <= data <= upper + max_extension):
                        closest_condition = condition
                        closest_distance = distance

            # Extend the closest condition to include the new data
            if closest_condition:
                lower, upper = self.known_conditions[self.category][closest_condition]
                new_lower = min(lower, data)
                new_upper = max(upper, data)
                self.known_conditions[self.category][closest_condition] = (new_lower, new_upper)
                print(f"Extended boundary of '{closest_condition}' to include new data: {new_lower} to {new_upper}")
            else:
                # Add new condition
                lower_bound = None
                upper_bound = None
                for condition_range in self.known_conditions[self.category].values():
                    if isinstance(condition_range, tuple):
                        # Check if data falls outside the lower boundary
                        if data > condition_range[1]:
                            lower_bound = condition_range[1]
                        # Check if data falls outside the upper boundary
                        elif data < condition_range[0] and (upper_bound is None or condition_range[0] < upper_bound):
                            upper_bound = condition_range[0]

                # Create a new range for the condition
                new_condition_range = (lower_bound + 0.1 if lower_bound is not None else data - 1, 
                                    upper_bound - 0.1 if upper_bound is not None else data + 1)

                # Create a new condition with this range
                new_condition_name = f"new_condition_{len(self.known_conditions[self.category]) + 1}"
                self.known_conditions[self.category][new_condition_name] = lambda x: new_condition_range[0] <= x <= new_condition_range[1]

    def tune_model_based_on_optimization_criteria(self):
        """ Calls the appropriate models based on optimization criteria (such as cost-efficiency) derived from machine. """
        model_configuration = {"precision": "model-1", "recall": "model-2"}
        self.model = model_configuration["precision"]


# data_processor = DataProcessing()
# state_adaptation = StateAdaptation()
# data_processor.on_data_processed.subscribe(state_adaptation)
# data_processor.process_data('battery')