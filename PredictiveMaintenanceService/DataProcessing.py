import pandas as pd

class DataProcessing:
    def process_data(self, raw_data):
        """
        Handles the overall data processing including cleaning and feature engineering.
        """
        clean_data = self.cleaning_data(raw_data)
        feature_data = self.feature_engineering(clean_data)
        return feature_data

    def cleaning_data(self, raw_data):
        """
        Performs data cleaning tasks like handling missing values, duplicates, etc.
        """
        cleaned_data = raw_data.dropna(axis=1, how='all')
        for i in range(1, 82):
            cleaned_data = cleaned_data.drop(columns=[f'Unnamed: {i}'], errors='ignore')
        cleaned_data.rename(columns={"Unnamed: 0": "Time"}, inplace=True)
        ref = cleaned_data["Time"][0]
        cleaned_data = cleaned_data.iloc[0:969]
        cleaned_data["ReferenceTime"] = cleaned_data.apply(lambda x: (x["Time"] - ref).total_seconds(), axis=1)
        col = cleaned_data.pop('ReferenceTime')
        cleaned_data.insert(1, col.name, col)
        return cleaned_data

    def feature_engineering(self, clean_data):
        """
        Applies various feature engineering techniques to the cleaned data.
        """
        window_size = 2
        feature_data = self.elapsed_time(clean_data)
        feature_data = self.rolling_mean(feature_data, 'DieselData.Fuelconsumption', window_size)
        feature_data = self.rolling_std(feature_data, 'DieselData.Speed', window_size)
        feature_data = self.change_in_sensor_readings(feature_data, 'DieselData.Fuelconsumption')
        feature_data = self.fuel_efficiency(feature_data, 'DieselData.Fuelconsumption', 'DieselData.OperatHours')
        feature_data = self.cumulative_operating_hours(feature_data, 'DieselData.OperatHours')
        feature_data = self.state_transitions(feature_data, 'MaschineStatus.WorkHydraulikAktiv')
        feature_data = self.pressure_difference(feature_data, 'Pumpe_Ibc_Obc_Druck.IbcP', 'Pumpe_Ibc_Obc_Druck.ObcP')
        return feature_data

    # Additional methods for each feature (elapsed_time, rolling_mean, etc.)

    # Functions for each feature
    def elapsed_time(self, df):
        df['Elapsed_Time_Feature'] = (df['Time'] - df['Time'].min()).dt.total_seconds()
        return df

    def rolling_mean(self, df, column_name, window_size):
        df[f'{column_name}_Rolling_Mean_Feature'] = df[column_name].rolling(window=window_size).mean()
        return df

    def rolling_std(self, df, column_name, window_size):
        df[f'{column_name}_Rolling_Std_Feature'] = df[column_name].rolling(window=window_size).std()
        return df

    def change_in_sensor_readings(self, df, column_name):
        df[f'{column_name}_Change_Feature'] = df[column_name].diff()
        return df

    def fuel_efficiency(self, df, fuel_col, hours_col):
        df['Fuel_Efficiency_Feature'] = df[fuel_col] / df[hours_col]
        return df

    def cumulative_operating_hours(self, df, column_name):
        df[f'{column_name}_Cumulative_Feature'] = df[column_name].cumsum()
        return df

    def state_transitions(self, df, column_name):
        df[f'{column_name}_State_Changes_Feature'] = df[column_name].diff().abs()
        return df

    def pressure_difference(self, df, pressure1, pressure2):
        df['Pressure_Difference_Feature'] = df[pressure1] - df[pressure2]
        return df
# Example usage of the DataProcessing class
data_processing_system = DataProcessing()
raw_data = pd.DataFrame()  # Replace with your actual DataFrame
processed_data = data_processing_system.process_data(raw_data)
