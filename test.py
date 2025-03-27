from src.test_data import g
from src.Reasoning import *

def main():
    g1 = g._copy_graph()
    g1.set_state("X4",1)
    g1.set_state("X6",2)
    g1.update_all_logic_state()
    
    sim_g = simplify_graph(g1)
    subgs = decompose_by_B(sim_g)

    for subg in subgs:
        print(calculate_evi_prob(subg))

if __name__ == '__main__':
    main()