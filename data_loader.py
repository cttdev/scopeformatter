from datetime import datetime
from enum import Enum
from io import StringIO

import numpy as np


class DataLoader:
    def __init__(self, file):
        self.load_file(file)

    def load_file(self, file):
        lines = open(file).readlines()
    
        self.date, self.start_time, self.data = self.process_raw_data_lines(lines)

    def get_date(self):
        return self.date
    
    def get_start_time(self):
        return self.start_time
    
    def get_data(self):
        return self.data

    @staticmethod
    def process_raw_data_lines(data):
        header_length = 5

        class IndexColumns(Enum):
            date = 0
            time = 1

        # Lambda to convert timestamp into datetime object.
        str_to_date_time = lambda x: datetime.strptime(x, '%H:%M:%S.%f')

        # Get the date and start time from the first line of the file.
        first_line = np.genfromtxt(StringIO(data[header_length]), dtype=None, encoding="utf-8", converters={IndexColumns.time.value: str_to_date_time}).tolist()
        date, start_time = first_line[:len(IndexColumns)]

        # Lambda to find delta between the timestamp datetime relative to the start time in seconds.
        str_to_delta_time = lambda x: (str_to_date_time(x) - start_time).microseconds * 1e-6

        output = np.genfromtxt(data, skip_header=header_length, encoding="utf-8", usecols=[i for i in range(len(IndexColumns)-1, len(first_line)-len(IndexColumns)+2)], converters={IndexColumns.time.value: str_to_delta_time})

        return date, start_time, output
