from typing import List, Any, Union

from ...data.entities import Node, Generator, Branch
from ...utils import logger


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
