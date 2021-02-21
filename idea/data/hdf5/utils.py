from typing import List, Any, Union

import pandas as pd
import numpy as np
from h5py import File

from idea.data.entities import Node, Generator, Branch
from idea.utils import logger

CLUSTER_COL_NAME = 'cluster'


def extract_node(node_values: List[Any]) -> Union[Node, None]:
    if len(node_values) != 3:
        logger.error('node values in nodes table have wrong number of elements 3!=%d'
                     % len(node_values))
        return None

    try:
        return Node(int(node_values[0]), int(node_values[1]), node_values[2])
    except ValueError as ve:
        logger.error(ve)
        return None


def extract_gen(gen_values: List[Any]) -> Union[Generator, None]:
    if len(gen_values) != 3:
        logger.error('gen values in gens table have wrong number of elements 3!=%d'
                     % len(gen_values))
        return None

    try:
        return Generator(int(gen_values[0]), gen_values[1], gen_values[2])
    except ValueError as ve:
        logger.error(ve)
        return None


def extract_branch(branch_values: List[Any]) -> Union[Branch, None]:
    if len(branch_values) != 3:
        logger.error('branch values in branches table have wrong number of elements 3!=%d'
                     % len(branch_values))
        return None

    try:
        return Branch(int(branch_values[0]), int(branch_values[1]), branch_values[2])
    except ValueError as ve:
        logger.error(ve)
        return None


TABLE_TO_EXTRACTOR = {
    'nodes': extract_node,
    'branches': extract_branch,
    'gens': extract_gen,
}


def get_table_df(hdf5_file: File, table_name: str, columns: List[str]) -> pd.DataFrame:
    columns_with_hour = columns[:] + ['hour']
    df = pd.DataFrame(columns=columns_with_hour, index=None)

    for hour in [x for x in hdf5_file.values()][0]:
        try:
            hour_int = int(hour.removeprefix('hour_'))
        except ValueError:
            logger.error('wrong hour format=%s != hour_{int}' % hour)
            continue

        hour_df = pd.DataFrame(columns=['node_from', 'node_to', 'flow'],
                               data=np.array(hdf5_file['results/' + hour + '/' + table_name]))
        hour_df['hour'] = [hour_int for _ in range(len(hour_df))]
        df = df.append(hour_df, ignore_index=True)

    return df
