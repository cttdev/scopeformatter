from enum import Enum
import numpy as np
from datetime import datetime

lines = open("test.txt").readlines()

header_length = 5

class Columns(Enum):
    date = 0
    time = 1
    voltage = 2

# Lambda to convert timestamp into datetime object.
str_to_date_time = lambda x: datetime.strptime(x, '%H:%M:%S.%f')

# Get the date and start time from the first line of the file.
date, start_time = np.genfromtxt(lines[:header_length+1], dtype=None, skip_header=header_length, encoding="utf-8", usecols=[Columns.date.value, Columns.time.value], converters={Columns.time.value: str_to_date_time}).tolist()

# Lambda to find delta between the timestamp datetime realtive to the start time in seconds.
str_to_delta_time = lambda x: (str_to_date_time(x) - start_time).microseconds * 1e-6

# Put the data to a numpy array.
data = np.genfromtxt(lines, skip_header=header_length, encoding="utf-8", usecols=[Columns.time.value, Columns.voltage.value], converters={Columns.time.value: str_to_delta_time})

print(data)

