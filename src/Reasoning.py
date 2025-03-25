from .model import *
from collections import defaultdict, deque

# 判断条件有向弧是否成立
def condition_satisfied(graph: DUCGGraph, condition):
        """
        论文里只提及了一种条件，仅含一个等号关系的条件
        """
        evidence = graph.state_info
        # 判断证据是否满足有向弧的条件
        is_satisfied = all(k in evidence and evidence[k] == v for k, v in condition)
        return is_satisfied

# 化简因果图
def simplify_graph(graph: DUCGGraph):
        """
         1) 若父、子节点观测到0, 则删除指向它的异常作用
         2) 若condition不满足, 删除该edge
        """
        new_nodes = {}
        new_edges = []
        for e in graph.edges:
            # 检查父节点
            parent_type = graph.nodes[e.parent].node_type
            if parent_type != 'B' and parent_type != 'G': # 如果有向弧涉及原因节点，则不检查父节点，因为提交证据时原因节点没有状态
                parent_st = graph.state_info.get(e.parent, None)
                if not parent_st:
                    continue
            
            # 检查子节点
            child_st = graph.state_info.get(e.child, None)
            if not child_st:
                continue

            # 检查条件F变量
            if e.condition and not condition_satisfied(graph, e.condition):
                continue

            new_edges.append(e) # 保留符合条件的有向弧
            # 保留合格有向弧的父子节点
            new_nodes[e.parent] = graph.nodes[e.parent]
            new_nodes[e.child] = graph.nodes[e.child]

        # 化简后的子图
        subg = DUCGGraph()
        subg.nodes = new_nodes
        subg.edges = new_edges
        subg.state_info = graph.abnormal_state

        return subg

# 广度优先搜索判断原因节点是否能解释所有异常证据
def has_path(graph: DUCGGraph, start, goal):
    # 邻接表
    graph_dict = graph.graph_dict # {'B1': ['X4'], 'B2': ['X4'], 'X4': ['X6']}

    visited = set() # 记录访问过的节点
    queue = deque([start]) # 访问路径
    while queue:
        curr = queue.popleft()
        if curr == goal:
            return True
        if curr not in visited:
            visited.add(curr)
            for nxt in graph_dict[curr]: # 把这个节点的相邻节点记录到访问路径中
                queue.append(nxt)
    return False

# 分解因果图
def decompose_by_B(graph: DUCGGraph):
    """
    只允许单一B_i=1
    针对所有B或D节点分别构造子图, 检查其能否解释全部异常.
    """
    # 找到异常节点
    # ab_node_names = []
    ab_node_names = graph.abnormal_state.keys()

    # 找到所有B和D节点
    bd_names = [n for n, node_obj in graph.nodes.items() if node_obj.node_type == "B" or node_obj.node_type == "D"]

    results = []
    for bd_name in bd_names:
        subg = graph._copy_graph()
        subg.state_info[bd_name] = 1

        can_explain = True
        for ab_node_name in ab_node_names:
            if not has_path(graph, bd_name, ab_node_name):
                can_explain = False
                break

        if can_explain:
            # 保留子图节点，仅含一个原因节点
            subg.nodes = {k: subg.nodes[k] for k in subg.state_info.keys()}
            
            # 保留分解后的有向弧
            graph_dict = graph.graph_dict
            graph_dict = {k: graph_dict[k] for k in subg.state_info.keys() if k in graph_dict}
            new_edges = []
            for e in subg.edges:
                if e.parent in graph_dict:
                    new_edges.append(e)
            subg.edges = new_edges
            subg.state_info.pop(bd_name)
            
            results.append(subg) # 保留能解释异常证据的子图
    
    return results