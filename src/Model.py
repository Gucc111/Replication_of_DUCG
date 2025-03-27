from collections import defaultdict
import copy

class DUCGNode:
    def __init__(self, name, node_type, prior_prob=None, logic_gate_spec=None):
        """
        name: 节点名
        node_type: 节点类型
        prior_prob: 若为B节点时，可存储先验概率
        logic_gate_spec: 若为G节点，可能需要存储门的定义
        """
        self.name = name
        self.node_type = node_type
        self.prior_prob = prior_prob   # 仅对B节点有效
        self.logic_gate_spec = logic_gate_spec  # 仅对G节点可能有效 {1: {'X3': 1, 'X5': 1}, 2: {'X3': 2, 'X5': 2}}

    def __repr__(self):
        return f"<DUCGNode {self.name}, type={self.node_type}>"

class DUCGEdge:
    def __init__(self, parent_name, child_name, weight=None, prob_matrix=None, condition=None):
        """
        parent: 父节点名
        child: 子节点类型
        condition: 条件表达式
        """
        self.parent = parent_name
        self.child = child_name
        self.condition = condition  # {'X3': 1}
        self.weight = weight
        self.prob_matrix = prob_matrix

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
    
    @property
    def graph_dict_ad(self):
        result = defaultdict(list)
        for e in self.edges:
            result[e.child].append(e.parent)
        return result
    
    @property
    def edges_dict_ad(self):
        result = defaultdict(list)
        for e in self.edges:
            result[e.child].append(e)
        return result
    
    @property
    def nodes_logic(self):
        nodes_logic = {}
        for name, node_obj in self.nodes.items():
            if node_obj.node_type == 'G':
                nodes_logic[name] = node_obj
        return nodes_logic
    
    def update_all_logic_state(self):
        for name, node_obj in self.nodes_logic.items():
            assigned_state = None
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
    
    def __getitem__(self, index):
        return self.nodes[index]