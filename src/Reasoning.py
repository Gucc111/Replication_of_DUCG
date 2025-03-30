from .Model import *
from collections import deque
import numpy as np

# 判断有向弧上的条件是否被当前图状态满足
def condition_satisfied(graph: DUCGGraph, condition: dict) -> bool:
    """
    检查边的 condition 条件是否被图中已知状态满足。
    目前仅支持“变量 == 某值”的逻辑。
    """
    evidence = graph.state_info
    return all(evidence.get(k) == v for k, v in condition.items())

# 对因果图进行结构简化：删除无法传递异常的有向弧和节点
def simplify_graph(graph: DUCGGraph) -> DUCGGraph:
    """
    化简原则：
    1. 子节点状态为0的边无效，剔除；
    2. 如果父节点不是B/D，且状态为0，也剔除；
    3. 如果边上的条件不满足，也剔除。
    """
    new_nodes = {}
    new_edges = []

    for e in graph.edges:
        # 检查父节点
        parent_type = graph.nodes[e.parent].node_type
        if parent_type not in ('B', 'D'): # 如果有向弧涉及原因节点，则不检查父节点，因为提交证据时原因节点没有状态
            if graph.state_info.get(e.parent, None) == 0:
                continue

        # 检查子节点
        if graph.state_info.get(e.child, None) == 0:
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

# 广度优先搜索：判断某个起点是否能通过图中路径达到目标
def has_path(graph: DUCGGraph, start: str, goal: str) -> bool:
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

# 将图按原因节点进行分解，构造可单独解释异常的子图
def decompose_by_B(graph: DUCGGraph) -> list[DUCGGraph]:
    """
    针对每个B或D类型节点，尝试构造仅激活该节点的图，
    并检查其能否解释所有异常状态。
    """
    # 找到所有异常证据
    ab_node_names = list(graph.abnormal_state.keys())
    # 找到所有B和D节点
    bd_names = list(graph.nodes_cause.keys())
    results = []

    for bd_name in bd_names:
        subg = graph._copy_graph()
        subg.set_state(bd_name, 1)
        can_explain = all(has_path(subg, bd_name, ab_node_name) for ab_node_name in ab_node_names)

        if can_explain:
            # 保留子图节点，仅含一个原因节点
            new_nodes = {k: v for k, v in subg.nodes.items() if k in subg.state_info}
            subg.nodes = new_nodes
            # 保留分解后的有向弧
            graph_dict = subg.graph_dict
            graph_dict = {k: graph_dict[k] for k in subg.state_info.keys()}
            new_edges = [e for e in subg.edges if e.parent in graph_dict]
            subg.edges = new_edges
            subg.state_info.pop(bd_name)
            results.append(subg) # 保留能解释异常证据的子图

    return results

# 计算子图中异常状态条件下的 Pr(E|H) 和联合概率 Pr(E,H)
def calculate_evi_prob(graph: DUCGGraph) -> tuple[float, float]:
    results = []
    
    for name, state in graph.state_info.items(): # 遍历异常证据
        edges2node = graph.edges_dict_ad[name] # 找到以这个节点为子节点的所有有向弧
        
        weights = [] # 保存每条有效弧的权重
        probs = [] # 保存父变量对子变量的因果作用概率
        for e in edges2node: # 遍历有向弧
            weights.append(e.weight)
            # 确定索引值，与父变量的状态有关，用于获取因果作用权重中的值
            idx = 1 if graph[e.parent].node_type in ('B', 'D') else graph.state_info[e.parent]
            probs.append(e.prob_matrix[state, idx])
        
        weights = np.array(weights)
        weights /= weights.sum() # 计算每条有效弧的相对权重
        probs = np.array(probs)
        cond_prob = (weights * probs).sum() # 对每条有向弧加权，计算多个父变量对同一个子变量的因果作用概率
        results.append(cond_prob)

    # 获取子图中原因变量的先验概率
    prior_prob = next(iter(graph.nodes_cause.values())).prior_prob 
    cond_total = np.prod(results)    
    return cond_total, cond_total * prior_prob

# 计算多个子图的状态概率与排序概率
def calculate_state_sort_probs(graph_list: list[DUCGGraph]) -> tuple[np.ndarray, np.ndarray]:
    subg_weights = []  # Pr(E|Hi)
    subg_post_prob = []  # Pr(Hi|E)

    for subg in graph_list:
        cond_prob, joint_prob = calculate_evi_prob(subg)
        subg_weights.append(cond_prob)
        subg_post_prob.append(joint_prob / cond_prob)

    # 计算每张子图的权重
    subg_weights = np.array(subg_weights)
    subg_weights /= subg_weights.sum()

    # 计算状态概率和排序概率
    subg_post_prob = np.array(subg_post_prob)
    state_prob = subg_weights * subg_post_prob
    sort_prob = state_prob / state_prob.sum()

    return state_prob, sort_prob