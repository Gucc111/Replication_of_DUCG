from .Model import *
import numpy as np

# 创建因果图
g = DUCGGraph()

# 添加节点变量
b1 = DUCGNode("B1", "B", prior_prob=0.1)
b2 = DUCGNode("B2", "B", prior_prob=0.05)
x3 = DUCGNode("X3", "X")
x4 = DUCGNode("X4", "X")
x5 = DUCGNode("X5", "X")
x6 = DUCGNode("X6", "X")
x7 = DUCGNode("X7", "X")
g8 = DUCGNode("G8", "G", logic_gate_spec={1: {'X3': 1, 'X5': 1}, 2: {'X3': 2, 'X5': 2}})
d9 = DUCGNode("D9", "D", prior_prob=0.05)
g.add_node(b1)
g.add_node(b2)
g.add_node(x3)
g.add_node(x4)
g.add_node(x5)
g.add_node(x6)
g.add_node(x7)
g.add_node(g8)
g.add_node(d9)

# 添加有向弧
e1 = DUCGEdge("B1","X3", weight=np.random.randint(1, 10), prob_matrix=np.random.rand(3, 2))
e2 = DUCGEdge("B1","X4", weight=np.random.randint(1, 10), prob_matrix=np.random.rand(3, 2))
e3 = DUCGEdge("B2","X4", weight=np.random.randint(1, 10), prob_matrix=np.random.rand(3, 2))
e4 = DUCGEdge("B2","X5", condition={'X3': 1}, weight=np.random.randint(1, 10), prob_matrix=np.random.rand(3, 2))  # 带条件
e5 = DUCGEdge("X3","G8", weight=np.random.randint(1, 10), prob_matrix=np.random.rand(3, 3))
e6 = DUCGEdge("X4","X6", weight=np.random.randint(1, 10), prob_matrix=np.random.rand(3, 3))
e7 = DUCGEdge("X5","G8", weight=np.random.randint(1, 10), prob_matrix=np.random.rand(3, 3))
e8 = DUCGEdge("G8","X7", weight=np.random.randint(1, 10), prob_matrix=np.random.rand(3, 3))
e9 = DUCGEdge("D9","X7", weight=np.random.randint(1, 10), prob_matrix=np.random.rand(3, 2))
e10 = DUCGEdge("X7","X6", weight=np.random.randint(1, 10), prob_matrix=np.random.rand(3, 3))
e11 = DUCGEdge("B1","X5", weight=np.random.randint(1, 10), prob_matrix=np.random.rand(3, 2))
g.add_edge(e1)
g.add_edge(e2)
g.add_edge(e11)
g.add_edge(e3)
g.add_edge(e4)
g.add_edge(e5)
g.add_edge(e6)
g.add_edge(e7)
g.add_edge(e8)
g.add_edge(e9)
g.add_edge(e10)