class Node:
    def __init__(self, node_id: int, size: float, color: float, node_type: int, desc: str):
        self.id = node_id
        self.size = size
        self.color = color
        self.type = node_type
        self.desc = desc


class Branch:
    def __init__(self, from_node: int, to_node: int, width: float, arrow_size: float):
        self.from_node = from_node
        self.to_node = to_node
        self.width = width
        self.arrow_size = arrow_size


class Arrow:
    def __init__(self, head_x: float, head_y: float, tail_x: float = 0,
                 tail_y: float = 0, size: float = 0, annotation: str = ''):
        self.head_x = head_x
        self.head_y = head_y
        self.tail_x = tail_x
        self.tail_y = tail_y
        self.size = size
        self._annotation = annotation

    def set_annotation(self, annotation: str):
        self._annotation = annotation

    def get_annotation(self) -> str:
        return self._annotation
