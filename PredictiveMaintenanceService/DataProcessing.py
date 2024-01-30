import pandas as pd
import logging
from functools import partial
from scipy.signal import savgol_filter
from sklearn.preprocessing import MinMaxScaler, StandardScaler
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from scipy.stats import zscore
import numpy as np

from utilities.observer_pattern import Event, Observer

#consider NAN values

class DataProcessing(Observer):
    def __init__(self):
        self.df_raw = None
        self.df_processed = None
        self.pipelines = {}
        self.on_data_processed = Event()
        self.logger = logging.getLogger('DataProcessing')
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        #Battery
        scale_voltage = partial(scale_value, column='Bat_Volt', min_value=0, max_value=10)
        battery_pipeline = [scale_voltage]
        self.register_pipeline('battery', battery_pipeline)

        #Fuel Filter
        fuel_pipeline = []  
        self.register_pipeline('fuel', fuel_pipeline)

        #Test
        # test_pipeline = []
        # self.register_pipeline('test', test_pipeline)

    def handle_event(self, accessed_data):
        self.df_raw = accessed_data
        self.df_processed = accessed_data
        self.process_data()
        # state_processed_data = self.df_processed.copy()
        # self.on_data_processed.emit(state_processed_data)
        self.df_processed = pd.Series()
        self.df_raw = pd.Series()

    def register_pipeline(self, data_type, subfunctions):
        """ Registers a sequence of subfunctions as a pipeline for a specific data type. """
        self.pipelines[data_type] = subfunctions

    def execute_pipeline(self, data_type):
        """ Executes the pipeline of subfunctions for a specific data type. """
        if data_type in self.pipelines:
            for subfunction in self.pipelines[data_type]:
                try:
                    self.df_processed = subfunction(self.df_processed)
                except Exception as e:
                    print("An error occurred in the pipeline execution.")
        else:
            self.logger.error(f"Empty pipeline registered for data type: {data_type}")

    def process_data(self):
        # self.df_processed["data_type"] = data_type
        """ Processes data according to the pipeline registered for its data type. """
        self.logger.info(f"Processing {self.df_processed['data_type']} data...")
        self.execute_pipeline(self.df_processed['data_type'])
        self.on_data_processed.emit(self.df_processed.copy())
        self.df_processed = pd.Series()

    def get_data(self):
        """
        Gets all processed data
        """
        return self.df_processed
    
    def update_subfunction(self, data_type, subfunction_name, new_subfunction):
        """ Updates a specific subfunction within a pipeline for a data type. """
        if data_type in self.pipelines:
            subfunctions = [subfunc for subfunc in self.pipelines[data_type] if subfunc.__name__ == subfunction_name]
            if subfunctions:
                # Assume there is only one subfunction with the given name in the pipeline
                index = self.pipelines[data_type].index(subfunctions[0])
                self.pipelines[data_type][index] = new_subfunction
            else:
                self.logger.error(f"Subfunction {subfunction_name} not found in {data_type} pipeline.")
        else:
            self.logger.error(f"No pipeline registered for data type: {data_type}")

# Time-dependent functions for each feature
def elapsed_time(self, df):
    df["Elapsed_Time_Feature"] = (df["Time"] - df["Time"].min()).dt.total_seconds()
    return df

def rolling_mean(self, df, column_name, window_size=10):
    df[f"{column_name}_Rolling_Mean_Feature"] = (
        df[column_name].rolling(window=window_size).mean()
    )
    return df

def rolling_std(self, df, column_name, window_size):
    df[f"{column_name}_Rolling_Std_Feature"] = (
        df[column_name].rolling(window=window_size).std()
    )
    return df

def change_in_sensor_readings(self, df, column_name):
    df[f"{column_name}_Change_Feature"] = df[column_name].diff()
    return df

def fuel_efficiency(self, df, fuel_col, hours_col):
    df["Fuel_Efficiency_Feature"] = df[fuel_col] / df[hours_col]
    return df

def cumulative_operating_hours(self, df, column_name):
    df[f"{column_name}_Cumulative_Feature"] = df[column_name].cumsum()
    return df

def state_transitions(self, df, column_name):
    df[f"{column_name}_State_Changes_Feature"] = df[column_name].diff().abs()
    return df

def difference(self, df, column1, column2):
    df[f"difference_between_{column1}_{column2}"] = df[column1] - df[column2]
    return df

def savgol(df, column, window_length=5, polyorder=2):
    df[f"savgol_{column}"] = savgol_filter(df[column], window_length, polyorder)
    return df

def detect_outliers(df, column):
    # Detect outliers using IQR
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    df = df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]
    return df

def scale_features(df):
    pass

def normalize_data(df):
    pass

def calculate_derivative(df, column, previous_value, time_elapsed):
    """ Calculates the derivative between two values given the time elapsed. """
    df[f"derivative_{column}"] = df[column].apply(lambda x: (x - previous_value) / time_elapsed)
    return df

# Features on single datapoint
def clip_value(df, column, min_value, max_value):
    """ Clips a value to a specified range. """
    df[f"clip_value{column}"] = df[column].apply(lambda x: max(min_value, min(max_value, x)))
    return df

# def scale_value(df, column, min_value, max_value):
#     """ Scales a single value using min-max scaling for a given column in a DataFrame. """
#     df[f"scale_value_{column}"] = df[column].apply(lambda x: (x - min_value) / (max_value - min_value))
#     return df

def scale_value(df, column, min_value, max_value):
    """ Scales a single value using min-max scaling. """
    if isinstance(df, pd.Series):
        df = df.to_frame().transpose()
        df[f"scale_value_{column}"] = df[column].apply(lambda x: (x - min_value) / (max_value - min_value))
        df = df.iloc[0]
    else:
        # Apply scaling as normal for DataFrame
        df[f"scale_value_{column}"] = df[column].apply(lambda x: (x - min_value) / (max_value - min_value))
    return df

def log_transform(df, column):
    """ Applies a logarithmic transform to the data in a specified column. """
    df[f"log_transform_{column}"] = df[column].apply(lambda x: np.log(x + 1))  # Adding 1 to avoid log(0)
    return df

# other
def standardize_column(df, column):
    """ Standardizes a specified column using z-score normalization. """
    df[column] = zscore(df[column])
    return df

def min_max_scale_column(df, column):
    """ Scales a specified column using min-max scaling. """
    scaler = MinMaxScaler()
    df[column] = scaler.fit_transform(df[[column]])
    return df

def impute_missing_values(df, column, strategy='mean'):
    """ Imputes missing values in a specified column using a given strategy. """
    imputer = SimpleImputer(strategy=strategy)
    df[column] = imputer.fit_transform(df[[column]])
    return df

def smooth_column(df, column, window_size=3):
    """ Smooths out a specified column using a rolling mean. """
    df[column] = df[column].rolling(window=window_size, min_periods=1).mean()
    return df

def calculate_correlation(df, column1, column2):
    """ Calculates the Pearson correlation coefficient between two columns. """
    return df[column1].corr(df[column2])

def fuse_data(df1, df2, on, how='inner'):
    """ Merges two datasets on a key column. """
    return pd.merge(df1, df2, on=on, how=how)

def extract_segment_features(df, column, start, end):
    """ Extracts features from a segment of a specified column. """
    segment = df[column].iloc[start:end]
    return {
        'mean': segment.mean(),
        'std': segment.std(),
        'max': segment.max(),
        'min': segment.min()
    }

def calculate_derivative(df, column):
    """ Calculates the first derivative of a specified column. """
    df[column + '_derivative'] = df[column].diff()
    return df

def apply_pca(df, n_components):
    """ Reduces the dimensionality of the dataset using PCA. """
    pca = PCA(n_components=n_components)
    principal_components = pca.fit_transform(df)
    return pd.DataFrame(data=principal_components)

# Extraction of Health Metrics

# System-Level Data Processing

# Component-Level Data Processing

# Feature Sets for State, Fault Diagnostics, Prognostics
        
# data_processor.process_data('fuel')
