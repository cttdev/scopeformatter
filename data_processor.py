

import numpy as np


class DataProcessor:
    def __init__(self, raw_data):
        self.raw_data = raw_data

        # Config Parameters
        self.data_extents = []
        self.x_divisor = 1
        self.y_divisor = 1
        self.decimation = 1
        self.zero_offset = False


    def get_raw_data(self):
        return self.raw_data

    def set_extents(self, x_lim, y_lim):
        self.data_extents = np.concatenate((x_lim, y_lim))


    def set_x_divisor(self, x_divisor):
        self.x_divisor = x_divisor


    def set_y_divisor(self, y_divisor):
        self.y_divisor = y_divisor


    def set_decimation(self, decimation):
        self.decimation = decimation
    

    def set_zero_offset(self, zero_offset):
        self.zero_offset = zero_offset


    def set_raw_data(self, raw_data):
        self.raw_data = raw_data
        

    def process_data(self):
        if self.raw_data.size == 0:
            return [], []

        # Extents
        updated_extents = self.data_extents.copy()
        
        # Apply Crop
        if not len(self.data_extents) == 0:
            crop = np.where(
                (self.raw_data[:, 0] >= self.data_extents[0]) &
                (self.raw_data[:, 0] <= self.data_extents[1]) &
                (self.raw_data[:, 1] >= self.data_extents[2]) &
                (self.raw_data[:, 1] <= self.data_extents[3])
            )
            cropped_data = self.raw_data[crop]
        else:
            cropped_data = self.raw_data

        # Apply Divisors
        divided_data = cropped_data / np.array([self.x_divisor, self.y_divisor])
        updated_extents = (np.array(updated_extents) / np.array([self.x_divisor, self.x_divisor, self.y_divisor, self.y_divisor])).tolist()

        # Apply Decimation
        decimated_data = divided_data[::self.decimation]

        # Apply Zero Offset
        if self.zero_offset:
            # Get min value from raw data
            min_value = min(self.raw_data[:, 1])

            # Apply zero offset to decimated data
            decimated_data[:, 1] = np.subtract(decimated_data[:, 1], min_value)

            # Update y-lims
            updated_extents[2:4] = updated_extents[2:4] - min_value

        return decimated_data, updated_extents
