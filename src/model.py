from collections import defaultdict
import copy

class DUCGNode:
    def __init__(self, name, node_type, states=None, prior_prob=None, logic_gate_spec=None):
        """
        name: 节点名
        node_type: 节点类型
        states: 节点可能的状态集
        prior_prob: 若为B节点时，可存储先验概率
        logic_gate_spec: 若为G节点，可能需要存储门的定义
        """
        self.name = name
        self.node_type = node_type
        self.states = states if states else []
        self.prior_prob = prior_prob   # 仅对B节点有效
        self.logic_gate_spec = logic_gate_spec  # 仅对G节点可能有效

    def __repr__(self):
        return f"<DUCGNode {self.name}, type={self.node_type}>"

class DUCGEdge:
    def __init__(self, parent_name, child_name, condition=None):
        """
        parent: 父节点名
        child: 子节点类型
        condition: 条件表达式
        """
        self.parent = parent_name
        self.child = child_name
        self.condition = condition  # {'X3': 1}

    def __repr__(self):
        cstr = f", cond={self.condition}" if self.condition else ""
        return f"<DUCGEdge {self.parent}->{self.child}{cstr}>"

class DUCGGraph:
    def __init__(self):
        self.nodes = {} # {节点名称: 节点实例}
        self.edges = []
        self.state_info = {} # {'X4': 2, 'X6': 1, 'X7': 0}

    # 添加节点
    def add_node(self, node: DUCGNode):
        self.nodes[node.name] = node

    # 添加有向弧
    def add_edge(self, edge: DUCGEdge):
        self.edges.append(edge)

    # 收到证据后添加变量状态
    def set_state(self, node_name, state):
        self.state_info[node_name] = state
    
    @property
    def abnormal_state(self):
        return {k:v for k, v in self.state_info.items() if v != 0}
    
    @property
    def graph_dict(self):
        result = defaultdict(list)
        for e in self.edges:
            result[e.parent].append(e.child)
        return result

    def _copy_graph(self):
        newg = DUCGGraph()

        for name, node_obj in self.nodes.items():
            newg.nodes[name] = copy.copy(node_obj)
        
        newg.edges = [copy.copy(e) for e in self.edges]
        
        newg.state_info = dict(self.state_info)
        return newg

    def __repr__(self):
        return (f"<DUCGGraph: {len(self.nodes)} nodes, {len(self.edges)} edges, "
                f"states={self.state_info}>")
