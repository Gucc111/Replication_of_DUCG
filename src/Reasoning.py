from .Model import *
from collections import deque
import numpy as np

# 判断条件有向弧是否成立
def condition_satisfied(graph: DUCGGraph, condition):
        """
        论文里只提及了一种条件，仅含一个等号关系的条件
        """
        evidence = graph.state_info
        # 判断证据是否满足有向弧的条件
        is_satisfied = all(k in evidence and evidence[k] == v for k, v in condition.items())
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
            if parent_type != 'B' and parent_type != 'D': # 如果有向弧涉及原因节点，则不检查父节点，因为提交证据时原因节点没有状态
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

# 计算某个子图中所有证据的联合概率Pr{E|H}和Pr{HE}
def calculate_evi_prob(graph: DUCGGraph):
    results = []
    
    for name, state in graph.state_info.items(): # 遍历异常证据
        edges2node = graph.edges_dict_ad[name] # 找到以这个节点为子节点的所有有向弧
        
        weights = [] # 保存每条有效弧的权重
        probs = [] # 保存父变量对子变量的因果作用概率
        for e in edges2node: # 遍历有向弧
            weights.append(e.weight)
            
            # 确定索引值，与父变量的状态有关，用于获取因果作用权重中的值
            if graph[e.parent].node_type != 'B' and graph[e.parent].node_type != 'D':
                idx = graph.state_info[e.parent]
            else: # 如果这条有向弧的父节点为原因变量，则自动把状态取为1，因为在提交异常证据时不会提交原因节点的状态，只能后向传播
                idx = 1
            probs.append(e.prob_matrix[state, idx])
        
        weights = np.array(weights)
        weights = weights / weights.sum() # 计算每条有效弧的相对权重
        probs = np.array(probs)

        cond_prob = (weights * probs).sum() # 对每条有向弧加权，计算多个父变量对同一个子变量的因果作用概率
        results.append(cond_prob)
    
    # 获取子图中原因变量的先验概率
    prior_prob = next(iter(graph.nodes_cause.values())).prior_prob 
    
    return np.prod(results), np.prod(results) * prior_prob

def calculate_state_sort_probs(graph_list: list):
    subg_weights = [] # 保存子图权重
    subg_post_prob = [] # 保存每个子图的后验概率
    for subg in graph_list:
        cond_prob, joint_prob = calculate_evi_prob(subg)
        post_prob = joint_prob / cond_prob # 计算后验概率
        subg_weights.append(cond_prob)
        subg_post_prob.append(post_prob)
    
    # 计算每张子图的权重
    subg_weights = np.array(subg_weights)
    subg_weights = subg_weights / subg_weights.sum()
    
    # 计算状态概率和排序概率
    subg_post_prob = np.array(subg_post_prob)
    state_prob = subg_weights * subg_post_prob
    sort_prob = state_prob / state_prob.sum()

    return state_prob, sort_prob