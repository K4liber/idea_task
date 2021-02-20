import math
from typing import Dict, Tuple

from .network_elements import Arrow


def get_arrow_from_branch(node_from: int, node_to: int, width: float,
                          nodes_pos: Dict[int, Tuple[float, float]]) -> Arrow:
    x0, y0 = nodes_pos[node_to]
    x1, y1 = nodes_pos[node_from]
    return Arrow(x0 + (x1 - x0)/2, y0 + (y1 - y0)/2, x1 - (x1 - x0)/4, y1 - (y1 - y0)/4, math.sqrt(width))


def size_scale(size: float) -> float:
    return math.sqrt(100*size)
