import pandas as pd
import logging

class DataProcessing:
    def __init__(self):
        self.processed_data = pd.DataFrame()

    def process_data(self, raw_data, append: bool=True):
        """
        Handles the overall data processing including cleaning and feature engineering.
        """
        logging.info("Processing data...")
        clean_data = self.__cleaning_data_row(raw_data)
        feature_data = self.__feature_engineering(clean_data)
        if append:
            self.processed_data = self.processed_data._append(feature_data, ignore_index=True)
        return feature_data
    
    def get_data(self):
        """
        Gets all processed data
        """
        return self.processed_data

    def __cleaning_data_row(self, data):
        """
        Performs on one row data cleaning tasks like handling missing values, duplicates, etc.
        """
        data.rename(columns={"Unnamed: 81": "Time"}, inplace=True)
        for i in range(0, 81):
            data = data.drop(columns=[f'Unnamed: {i}'], errors='ignore')
        try:
            if not self.get_data().empty:
                data = pd.DataFrame([data.reindex(columns=self.get_data().columns).iloc[0]])
                ref = self.get_data()["Time"][0]
                data = data[self.get_data().columns]
                data["ReferenceTime"] = data.apply(lambda x: (x["Time"] - ref).total_seconds(), axis=1)
            else:
                data["ReferenceTime"] = 0
                # col = cleaned_data.pop('ReferenceTime')
                # cleaned_data.insert(1, col.name, col)
        except KeyError:
            print("KeyError")
            return 0
        return data
    
    def __cleaning_data_all(self, raw_data):
        """
        Performs data cleaning tasks on all data
        """
        cleaned_data = raw_data.dropna(axis=1, how='all')
        for i in range(1, 82):
            cleaned_data = cleaned_data.drop(columns=[f'Unnamed: {i}'], errors='ignore')
        cleaned_data.rename(columns={"Unnamed: 0": "Time"}, inplace=True)
        ref = cleaned_data["Time"][0]
        cleaned_data["ReferenceTime"] = cleaned_data.apply(lambda x: (x["Time"] - ref).total_seconds(), axis=1)
        # col = cleaned_data.pop('ReferenceTime')
        # cleaned_data.insert(1, col.name, col)
        return cleaned_data

    def __feature_engineering(self, clean_data):
        """
        Applies various feature engineering techniques to the cleaned data.
        """
        window_size = 2
        feature_data = self.__elapsed_time(clean_data)
        feature_data = self.__rolling_mean(feature_data, 'DieselData.Fuelconsumption', window_size)
        feature_data = self.__rolling_std(feature_data, 'DieselData.Speed', window_size)
        feature_data = self.__change_in_sensor_readings(feature_data, 'DieselData.Fuelconsumption')
        feature_data = self.__fuel_efficiency(feature_data, 'DieselData.Fuelconsumption', 'DieselData.OperatHours')
        feature_data = self.__cumulative_operating_hours(feature_data, 'DieselData.OperatHours')
        feature_data = self.__state_transitions(feature_data, 'MaschineStatus.WorkHydraulikAktiv')
        feature_data = self.__pressure_difference(feature_data, 'Pumpe_Ibc_Obc_Druck.IbcP', 'Pumpe_Ibc_Obc_Druck.ObcP')
        return feature_data

    # Functions for each feature
    def __elapsed_time(self, df):
        df['Elapsed_Time_Feature'] = (df['Time'] - df['Time'].min()).dt.total_seconds()
        return df

    def __rolling_mean(self, df, column_name, window_size):
        df[f'{column_name}_Rolling_Mean_Feature'] = df[column_name].rolling(window=window_size).mean()
        return df

    def __rolling_std(self, df, column_name, window_size):
        df[f'{column_name}_Rolling_Std_Feature'] = df[column_name].rolling(window=window_size).std()
        return df

    def __change_in_sensor_readings(self, df, column_name):
        df[f'{column_name}_Change_Feature'] = df[column_name].diff()
        return df

    def __fuel_efficiency(self, df, fuel_col, hours_col):
        df['Fuel_Efficiency_Feature'] = df[fuel_col] / df[hours_col]
        return df

    def __cumulative_operating_hours(self, df, column_name):
        df[f'{column_name}_Cumulative_Feature'] = df[column_name].cumsum()
        return df

    def __state_transitions(self, df, column_name):
        df[f'{column_name}_State_Changes_Feature'] = df[column_name].diff().abs()
        return df

    def __pressure_difference(self, df, pressure1, pressure2):
        df['Pressure_Difference_Feature'] = df[pressure1] - df[pressure2]
        return df
