from collections import defaultdict
import copy
import numpy as np

class DUCGNode:
    def __init__(self, name: str, node_type: str, prior_prob: float = None, logic_gate_spec: dict = None):
        # 节点名
        self.name = name
        # 节点类型（B: 原因节点，X: 中间节点，G: 逻辑门节点）
        self.node_type = node_type
        # 先验概率（仅对原因节点B有效）
        self.prior_prob = prior_prob
        # 逻辑门定义（仅对G节点有效），如 {1: {"X3": 1, "X5": 1}}
        self.logic_gate_spec = logic_gate_spec

    def __repr__(self):
        return f"<DUCGNode {self.name}, type={self.node_type}>"

class DUCGEdge:
    def __init__(self, parent_name: str, child_name: str, weight: float, prob_matrix, condition=None):
        # 父节点名称
        self.parent = parent_name
        # 子节点名称
        self.child = child_name
        # 有向弧的权重
        self.weight = weight
        # 条件概率矩阵（二维数组）
        self.prob_matrix = np.array(prob_matrix) if isinstance(prob_matrix, list) else prob_matrix
        # 条件限制（如 {"X3": 1}）
        self.condition = condition

    def __repr__(self):
        cstr = f", cond={self.condition}" if self.condition else ""
        return f"<DUCGEdge {self.parent}->{self.child}{cstr}>"

class DUCGGraph:
    def __init__(self):
        # 所有节点（键为节点名，值为节点实例）
        self.nodes = {}
        # 所有有向弧的列表
        self.edges = []
        # 节点的状态信息（如 {'X1': 1}）
        self.state_info = {}

    # 支持添加单个、多个（列表/元组）、或字典形式的节点
    def add_node(self, node_or_nodes):
        if isinstance(node_or_nodes, DUCGNode):
            self.nodes[node_or_nodes.name] = node_or_nodes
        elif isinstance(node_or_nodes, (list, tuple)):
            for node_obj in node_or_nodes:
                if not isinstance(node_obj, DUCGNode):
                    raise TypeError(f'Expected DUCGNode, but got {type(node_obj).__name__} instead.')
                self.nodes[node_obj.name] = node_obj
        elif isinstance(node_or_nodes, dict):
            for name, node_obj in node_or_nodes.items():
                if not isinstance(node_obj, DUCGNode):
                    raise TypeError(f'Expected DUCGNode, but got {type(node_obj).__name__} instead.')
                self.nodes[name] = node_obj
        else:
            raise TypeError('add_node() accepts DUCGNode, list/tuple of DUCGNode or dict of DUCGNode.')

    # 支持添加单条、多条（列表/元祖）有向弧
    def add_edge(self, edge_or_edges):
        if isinstance(edge_or_edges, DUCGEdge):
            self.edges.append(edge_or_edges)
        elif isinstance(edge_or_edges, (list, tuple)):
            for edge in edge_or_edges:
                if not isinstance(edge, DUCGEdge):
                    raise TypeError(f'Expected DUCGEdge, but got {type(edge).__name__} instead.')
                self.edges.append(edge)
        else:
            raise TypeError('add_edge() accepts DUCGEdge, list/tuple of DUCGEdge.')
    
    # 快速构图，同时添加节点和边
    def build_graph(self, nodes=None, edges=None):
        if nodes:
            self.add_node(nodes)
        if edges:
            self.add_edge(edges)
    
    # 从 JSON 构建图
    @classmethod
    def from_dict(cls, data: dict):
        graph = cls()
        # 添加节点
        for node_info in data.get('nodes', []):
            spec = node_info.get('logic_gate_spec')
            node = DUCGNode(
                name=node_info['name'],
                node_type=node_info['node_type'],
                prior_prob=node_info.get('prior_prob'),
                logic_gate_spec={int(k): v for k, v in spec.items()} if spec is not None else None
            )
            graph.add_node(node)
        # 添加有向弧
        for edge_info in data.get('edges', []):
            edge = DUCGEdge(
                parent_name=edge_info['parent_name'],
                child_name=edge_info['child_name'],
                weight=edge_info['weight'],
                prob_matrix=np.array(edge_info['prob_matrix']),
                condition=edge_info.get('condition')
            )
            graph.add_edge(edge)
        return graph
    
    # 将图导出为 JSON 可序列化字典
    def to_dict(self):
        return {
            "nodes": [
                {
                    "name": node.name,
                    "node_type": node.node_type,
                    "prior_prob": node.prior_prob if node.prior_prob is not None else None,
                    "logic_gate_spec": node.logic_gate_spec if node.logic_gate_spec is not None else None
                }
            for node in self.nodes.values()
            ],
            "edges": [
                {
                    "parent_name": edge.parent_name,
                    "child_name": edge.child_name,
                    "weight": edge.weight,
                    "prob_matrix": edge.prob_matrix.tolist(),
                    "condition": edge.condition if edge.condition is not None else None
                }
            for edge in self.edges
            ]
        }

    # 设置节点状态值
    def set_state(self, node_name, state):
        self.state_info[node_name] = state

    def _copy_graph(self):
        newg = DUCGGraph()
        newg.nodes = {k: copy.copy(v) for k, v in self.nodes.items()}
        newg.edges = [copy.copy(e) for e in self.edges]
        newg.state_info = dict(self.state_info)
        return newg

    def __getitem__(self, index):
        return self.nodes[index]

    def __repr__(self):
        return (f"<DUCGGraph: {len(self.nodes)} nodes, {len(self.edges)} edges, "
                f"states={self.state_info}>")

    # 返回所有非零状态的节点（即异常状态）
    @property
    def abnormal_state(self):
        return {k: v for k, v in self.state_info.items() if v != 0}

    # 正向图结构（父→子）
    @property
    def graph_dict(self):
        result = defaultdict(list)
        for e in self.edges:
            result[e.parent].append(e.child)
        return result

    # 反向图结构（子→父）
    @property
    def graph_dict_ad(self):
        result = defaultdict(list)
        for e in self.edges:
            result[e.child].append(e.parent)
        return result

    # 父节点 → 出边集合
    @property
    def edges_dict(self):
        result = defaultdict(list)
        for e in self.edges:
            result[e.parent].append(e)
        return result

    # 子节点 → 入边集合
    @property
    def edges_dict_ad(self):
        result = defaultdict(list)
        for e in self.edges:
            result[e.child].append(e)
        return result

    # 所有原因节点（类型为 'B'）
    @property
    def nodes_cause(self):
        return {name: node_obj for name, node_obj in self.nodes.items() if node_obj.node_type in ('B', 'D')}

    # 所有逻辑门节点（类型为 'G'）
    @property
    def nodes_logic(self):
        return {name: node_obj for name, node_obj in self.nodes.items() if node_obj.node_type == 'G'}

    # 更新所有逻辑门节点的状态值（根据其父节点状态）
    def update_all_logic_state(self):
        for name, node_obj in self.nodes_logic.items():
            assigned_state = None
            # 所有父节点状态都已知时，才尝试匹配门逻辑
            is_satisfied = all(parent in self.state_info for parent in self.graph_dict_ad[name])
            if is_satisfied:
                assigned_state = 0
                for state, condspec in node_obj.logic_gate_spec.items():
                    matched = all(self.state_info[n] == s for n, s in condspec.items())
                    if matched:
                        assigned_state = state
                        break
            if assigned_state is not None:
                self.set_state(name, assigned_state)
