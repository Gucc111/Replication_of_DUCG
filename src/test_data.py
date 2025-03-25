from .model import *

# 创建因果图
g = DUCGGraph()

# 添加节点变量
b1 = DUCGNode("B1", "B", states=[0,1], prior_prob=0.1)
b2 = DUCGNode("B2", "B", states=[0,1], prior_prob=0.05)
x3 = DUCGNode("X3", "X", states=[0,1,2])
x4 = DUCGNode("X4", "X", states=[0,1,2])
x5 = DUCGNode("X5", "X", states=[0,1,2])
x6 = DUCGNode("X6", "X", states=[0,1,2])
x7 = DUCGNode("X7", "X", states=[0,1,2])
g8 = DUCGNode("G8", "G", states=[0,1,2], logic_gate_spec={1: {'X3': 1, 'X5': 1}, 2: {'X3': 2, 'X5': 2}})
d9 = DUCGNode("D9", "D", states=[0,1], prior_prob=0.05)
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
e1 = DUCGEdge("B1","X3")
e2 = DUCGEdge("B1","X4")
e3 = DUCGEdge("B2","X4")
e4 = DUCGEdge("B2","X5", condition={'X3': 1})  # 带条件
e5 = DUCGEdge("X3","G8")
e6 = DUCGEdge("X4","X6")
e7 = DUCGEdge("X5","G8")
e8 = DUCGEdge("G8","X7")
e9 = DUCGEdge("D9","X7")
e10 = DUCGEdge("X7","X6")
g.add_edge(e1)
g.add_edge(e2)
g.add_edge(e3)
g.add_edge(e4)
g.add_edge(e5)
g.add_edge(e6)
g.add_edge(e7)
g.add_edge(e8)
g.add_edge(e9)
g.add_edge(e10)

g.set_state("X3",1)
g.set_state("X5",1)
g.update_all_logic_state()