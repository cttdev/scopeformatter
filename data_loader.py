import math
from datetime import datetime
from enum import Enum
from io import StringIO
from sqlite3 import converters

import numpy as np


class DataLoader:
    def __init__(self, file):
        self.load_file(file)

    def load_file(self, file):
        lines = open(file).readlines()
    
        self.dates, self.start_times, self.data = self.process_txt_data_lines(lines)

    def get_dates(self):
        return self.dates
    
    def get_start_times(self):
        return self.start_times
    
    def get_data(self):
        return self.data

    def get_series_dict(self):
        series_dict = {}

        for i in range(self.data.shape[1]):
            if (i + self.DataColums.Voltage.value) % 2 == 0:
                series_dict["Voltage " + str(math.floor(i / 2))] = i
            else:
                series_dict["Time " + str(math.floor(i / 2))] = i
        
        return series_dict

    def get_num_voltage_columns(self):
        return self.data.shape[1] - len(self.IndexColumns)

    def process_txt_data_lines(self, raw_data):
        dates = []
        start_times = []

        header_length = 5

        labels = np.genfromtxt(StringIO(raw_data[header_length-1]), dtype=None, encoding="utf-8").tolist()
        num_series = sum("Y" in i for i in labels)

        # Lambda to convert timestamp into datetime object.
        str_to_date_time = lambda x: datetime.strptime(x, '%H:%M:%S.%f')

        first_line_converters = {}
        for i in range(num_series):
            first_line_converters[self.Columns.time.value + i*len(self.Columns)] = str_to_date_time

        # Get the date and start time from the first line of the file.
        first_line = np.genfromtxt(StringIO(raw_data[header_length]), dtype=None, encoding="utf-8", converters=first_line_converters).tolist()
        num_series = math.floor(len(first_line)/len(self.Columns))

        for i in range(num_series):
            date, start_time, voltage = first_line[i*len(self.Columns):(i+1)*len(self.Columns)]
            dates.append(date)
            start_times.append(start_time)

        # Lambda to find delta between the timestamp datetime relative to the start time in seconds.
        # NOTE: ALL TIMESTAMPS (FOR BOTH SERIES) ARE RELATIVE TO THE SMALLEST TIMESTAMP IN THE FILE.
        str_to_delta_time = lambda x: (str_to_date_time(x) - min(start_times)).microseconds * 1e-6

        data_converters = {}
        for i in range(num_series):
            data_converters[self.Columns.time.value + i*len(self.Columns)] = str_to_delta_time

        cols = []
        for i in range(num_series):
            cols.append(self.Columns.time.value + i*len(self.Columns))
            cols.append(self.Columns.voltage.value + i*len(self.Columns))

        output = np.genfromtxt(raw_data, skip_header=header_length, encoding="utf-8", usecols=cols, converters=data_converters)

        return dates, start_times, output
    
    # In raw data txt
    class Columns(Enum):
        date = 0
        time = 1
        voltage = 2

    # In processed data array
    class DataColums(Enum):
        Time = 0
        Voltage = 1

if __name__ == "__main__":
    data = DataLoader("test2.txt")
    print(data.get_data())
