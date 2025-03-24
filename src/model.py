from collections import defaultdict, deque
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
        self.parent = parent_name
        self.child = child_name
        self.condition = condition  # 字符串或其他形式均可

    def __repr__(self):
        cstr = f", cond={self.condition}" if self.condition else ""
        return f"<DUCGEdge {self.parent}->{self.child}{cstr}>"

class DUCGGraph:
    def __init__(self):
        self.nodes = {}
        self.edges = []
        self.state_info = {}

    def add_node(self, node: DUCGNode):
        self.nodes[node.name] = node

    def add_edge(self, edge: DUCGEdge):
        self.edges.append(edge)

    def set_state(self, node_name, state):
        self.state_info[node_name] = state

    def simplify_graph(self):
        """
         1) 若父、子节点观测到0, 则删除指向它的异常作用
         2) 若condition不满足, 删除该edge
        """
        new_edges = []
        for e in self.edges:
            # 检查子节点
            child_st = self.state_info.get(e.child, None)
            if child_st == 0:
                continue

            # 检查父节点
            parent_st = self.state_info.get(e.parent, None)
            if parent_st == 0:
                continue

            # 检查条件F变量
            if e.condition and not self._condition_satisfied(e.condition):
                continue

            new_edges.append(e)
        self.edges = new_edges

    def _condition_satisfied(self, cond_str):
        """
        解析条件表达式, 如 "X3=1".
        论文里暂时只提及了仅含一个等号关系的条件
        """
        if "=" not in cond_str:
            # 后续补充
            return True

        var, val = cond_str.split("=")
        var, val = var.strip(), val.strip()
        if var in self.state_info:
            actual_st = self.state_info[var]
            try:
                val_int = int(val)
            except:
                return False
            return (actual_st == val_int)
        # 如果没有该变量的观测, 暂视为不满足
        return False

    def decompose_by_B(self):
        """
        若只允许单一B_i=1,
        则针对所有B或D节点分别构造子图, 检查其能否解释全部异常.
        """
        # 找到异常节点
        abnormal_nodes = []
        for n, st in self.state_info.items():
            if st is not None and st != 0:
                abnormal_nodes.append(n)

        # 找到所有B和D节点
        b_names = [n for n,node_obj in self.nodes.items() if node_obj.node_type=="B" or node_obj.node_type=="D"]

        results = []
        for b_name in b_names:
            subg = self._copy_graph()
            subg.state_info[b_name] = 1

            can_explain = True
            for abn in abnormal_nodes:
                if not subg._has_path(b_name, abn):
                    can_explain = False
                    break

            results.append((b_name, subg, can_explain))
        return results

    def _has_path(self, start, goal):
        graph_dict = defaultdict(list)
        for e in self.edges:
            graph_dict[e.parent].append(e.child)

        visited = set()
        queue = deque([start])
        while queue:
            curr = queue.popleft()
            if curr == goal:
                return True
            if curr not in visited:
                visited.add(curr)
                for nxt in graph_dict[curr]:
                    queue.append(nxt)
        return False

    def _copy_graph(self):
        newg = DUCGGraph()

        for name,node_obj in self.nodes.items():
            newg.nodes[name] = copy.copy(node_obj)
        
        newg.edges = [copy.copy(e) for e in self.edges]
        
        newg.state_info = dict(self.state_info)
        return newg

    def __repr__(self):
        return (f"<DUCGGraph: {len(self.nodes)} nodes, {len(self.edges)} edges, "
                f"states={self.state_info}>")
