from .Model import *
import numpy as np
import json

# 创建因果图
with open('/Users/gucc1/Documents/Codes/Replication_of_DUCG/Data/ducg_graph.json', 'r') as f:
    graph_data = json.load(f)
g = DUCGGraph.from_dict(graph_data)
