from .model import *

g = DUCGGraph()

b1 = DUCGNode("B1", "B", states=[0,1], prior_prob=0.1)
b2 = DUCGNode("B2", "B", states=[0,1], prior_prob=0.05)
d9 = DUCGNode("D9", "D", states=[0,1], prior_prob=0.05)
x4 = DUCGNode("X4", "X", states=[0,1,2])  # normal=0, abnormal=1/2
x6 = DUCGNode("X6", "X", states=[0,1,2])
x7 = DUCGNode("X7", "X", states=[0,1,2])

g.add_node(b1)
g.add_node(b2)
g.add_node(d9)
g.add_node(x4)
g.add_node(x6)
g.add_node(x7)

# 添加有向边
e1 = DUCGEdge("B1","X4")  # 无条件
e2 = DUCGEdge("B2","X4")  # 无条件
e3 = DUCGEdge("B2","X6", condition="X3=1")  # 带条件
e4 = DUCGEdge("X4","X6")  # 无条件
e5 = DUCGEdge("D9","X7")  # e.g. X6=2->X7=?
e6 = DUCGEdge("X7","X6")  # e.g. X6=2->X7=?
g.add_edge(e1)
g.add_edge(e2)
g.add_edge(e3)
g.add_edge(e4)
g.add_edge(e5)
g.add_edge(e6)

# 2. 设定观测到的证据: X4=1(异常1), X6=2(异常2), X7=0(正常)
g.set_state("X4",1)
g.set_state("X6",2)
g.set_state("X7",0)