from typing import List

import pandas as pd
import numpy as np


file: str = 'C:/Users/fayfo/Desktop/数据.xlsx'
data_a = pd.read_excel(file, sheet_name='Sheet1', dtype='str')
# data_b = pd.read_excel(file, sheet_name='Sheet2', dtype='str')

rules = [
            [[1, 1, 15], [2, 1, 1]],
            [[1, 1, 15], [3, 1, 1]]
        ],

data: List[int] = np.array(data_a)


def check(pending: List[List[int]], rule: List[List[int]]):
    for i in range(len(pending)):
        for j in range(len(pending[i])):
            print(pending[i][j])
