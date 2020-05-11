import json
from typing import List, Dict

from src.graph.edge import Edge
from src.graph.node import Node


class Graph:
    def __init__(self):
        self.edges: Dict[int, Edge] = {}
        self.nodes: Dict[int, Node] = {}
        self.marker: tuple = ()

    def __repr__(self):
        return str(self.to_dict())

    def add_marker(self, name: str, value):
        self.marker: tuple = (name, value)

    def to_dict(self) -> dict:
        return {
            "nodes": [node.to_dict() for node in self.nodes.values()],
            "edges": [edge.to_dict() for edge in self.edges.values()]
        }

    def save_as_json(self, path: str = 'data/graph.json') -> None:
        with open(path, "w+") as f:
            f.write(json.dumps(self.to_dict()))

    def create_edge(self, node_1_id: int, node_2_id: int):
        if node_1_id not in self.nodes or node_2_id not in self.nodes:
            return
        node_1 = self.nodes[node_1_id]
        node_2 = self.nodes[node_2_id]

        # Check if nodes are already in graph
        if node_1 not in self.nodes.values():
            self.nodes[node_1.id] = node_1
        if node_2 not in self.nodes.values():
            self.nodes[node_2.id] = node_2

        edge_1 = Edge(node_1, node_2, len(self.edges) + 1)
        edge_2 = Edge(node_2, node_1, len(self.edges) + 1)

        # check if edge is already in graph
        if edge_1 not in self.edges.values():
            self.edges[edge_1.id] = edge_1

        # check if edge is already in connected nodes
        if edge_1 not in self.nodes[node_1.id].edges:
            self.nodes[node_1.id].edges.append(edge_1)

        # check if edge is already in connected nodes
        if edge_2 not in self.nodes[node_2.id].edges:
            self.nodes[node_2.id].edges.append(edge_2)

    def add_node(self, node: Node):
        if node not in self.nodes.values():
            self.nodes[node.id] = node
        else:
            self.nodes[node.id].x = node.x
            self.nodes[node.id].y = node.y

    def set_node_label(self, node_id: int, label: str):
        if node_id in self.nodes:
            self.nodes[node_id].label = label

    def set_edge_label(self, edge_id: int, label: str):
        if edge_id in self.edges:
            self.edges[edge_id].label = label
        for i in range(0, len(self.nodes[self.edges[edge_id].source.id].edges)):
            self.nodes[self.edges[edge_id].source.id].edges[i].label = label
        for i in range(0, len(self.nodes[self.edges[edge_id].target.id].edges)):
            self.nodes[self.edges[edge_id].target.id].edges[i].label = label

    def _to_dict(self):
        matrix_dict: dict = {}
        for node_1 in self.nodes.values():
            matrix_dict[node_1.id] = {}
            for node_2 in self.nodes.values():
                matrix_dict[node_1.id][node_2.id] = 0

        for edge in self.edges.values():
            matrix_dict[edge.source.id][edge.target.id] = 1
            matrix_dict[edge.target.id][edge.source.id] = 1
        return matrix_dict

    def _to_matrix(self):
        matrix_dict = self._to_dict()

        result: list = []
        for key_1 in matrix_dict:
            result.append([1])
            for key_2 in matrix_dict[key_1]:
                result[len(result) - 1].append(matrix_dict[key_1][key_2])
        return result

    def _to_reduced_matrix(self):
        result = self._to_matrix()
        i: int = 0
        while i < len(result):
            j: int = i + 1
            while j < len(result[i]):
                del result[i][j]
            i += 1
        return result

    def max_edges(self):
        result: int = 0
        for node in self.nodes.values():
            if len(node.edges) > result:
                result = len(node.edges)
        return result

    def is_cyclic(self) -> bool:
        if len(self.nodes) != len(self.edges):
            return False

        matrix: List[list] = self._to_reduced_matrix()

        # cut first column
        matrix.pop(0)
        for row in matrix:
            del row[0]

        # check axis
        i: int = 0
        while i < len(matrix):
            if matrix[i][i] == 0:
                return False
            i += 1

        # check left lower corner
        if matrix[i - 1][0] == 0:
            return False

        return True

    def is_path(self) -> bool:
        if len(self.marker) != 0 and self.marker[0] == 'is_path' and self.marker[1] == True:
            return True

        if len(self.edges) != len(self.nodes) - 1:
            return False

        matrix: List[list] = self._to_reduced_matrix()

        # cut first column
        matrix.pop(0)
        for row in matrix:
            del row[0]

        # check axis
        i: int = 0
        while i < len(matrix):
            if matrix[i][i] == 0:
                return False
            i += 1

        return True

    def is_complete(self):
        matrix: List[list] = self._to_reduced_matrix()
        for row in matrix:
            for cell in row:
                if cell != 1:
                    return False
        return True

    def is_vmtl(self) -> bool:
        previous_k = None
        for node in self.nodes.values():
            current_k = sum([int(node.label)] + [int(edge.label) for edge in node.edges])
            if current_k != previous_k and previous_k is not None:
                return False
        return True

    @staticmethod
    def generate_cyclic(n: int):
        graph = Graph()
        for i in range(1, n + 1):
            graph.add_node(Node(i))
        for i in range(1, n + 1):
            graph.create_edge(i, i % n + 1)
        return graph

    @staticmethod
    def generate_path(n: int):
        graph = Graph()
        for i in range(1, n + 1):
            graph.add_node(Node(i))
        for i in range(1, n):
            graph.create_edge(i, i + 1)
        return graph

    @staticmethod
    def generate_complete(n: int):
        graph = Graph()
        for i in range(1, n + 1):
            graph.add_node(Node(i))
        for i in range(1, n + 1):
            for j in range(1, n + 1):
                if i == j:
                    break
                graph.create_edge(i, j)
        return graph
