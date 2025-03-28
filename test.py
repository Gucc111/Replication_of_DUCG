from src.test_data import g
from src.Reasoning import *

def main():
    g1 = g._copy_graph()
    g1.set_state("X3", 2)
    g1.set_state("X4", 1)
    g1.set_state("X5", 2)
    g1.set_state("X6", 2)
    g1.set_state("X7", 0)
    g1.update_all_logic_state()
    
    sim_g = simplify_graph(g1)
    subgs = decompose_by_B(sim_g)

    results = calculate_state_sort_probs(subgs)
    print(results)

    print("初始图:", g1)
    print("Edges:")
    for ed in g1.edges:
        print("  ", ed)

    print("\n化简后图:", sim_g)
    print("Edges:")
    for ed in sim_g.edges:
        print("  ", ed)

    for i in range(len(subgs)):
        print(f"\n分解后子图{i+1}:", subgs[i])
        print("Edges:")
        for ed in subgs[i].edges:
            print("  ", ed)

if __name__ == '__main__':
    main()