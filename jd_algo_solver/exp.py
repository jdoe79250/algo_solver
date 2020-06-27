"""
Experiments
"""
import logging.config
import os
import sys
import pickle
import pprint

from distriopt import SolutionStatus
from distriopt import VirtualNetwork
from distriopt.embedding import PhysicalNetwork
from distriopt.embedding.algorithms import (
    EmbedGreedy,
    EmbedPartition,
    EmbedILP,
    EmbedBalanced,
)


logging.basicConfig(
    stream=sys.stdout,
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

log = logging.getLogger(__name__)


def time_comparison_grid5000(timelimit, net_type="fat-tree"):
    """
    Custom Network  (for the moment fat tree and random are available on virtual.py)
    """
    # create the physical network representation
    physical = PhysicalNetwork.from_files("grisou")

    solvers_ilp = {"cplex"}
    solvers_heu = {
        "GreedyPartition": EmbedGreedy,
        "k-balanced": EmbedBalanced,
        "DivideSwap": EmbedPartition,
    }

    res_experiments = {"x": [], "time": {}, "value": {}}
    for method_name in solvers_ilp | solvers_heu.keys():
        res_experiments["time"][method_name] = {}
        res_experiments["value"][method_name] = {}

    if net_type == "fat-tree":
        min_v = 2
        max_v = 12
        step_size = 2
    elif net_type == "random":
        min_v = 25
        max_v = 175
        step_size = 25
    else:
        raise ValueError("invalid experiment type")

    for v in range(min_v, max_v + 1, step_size):
        res_experiments["x"].append(v)

        if net_type == "fat-tree":
            virtual = VirtualNetwork.create_fat_tree(v)
        else:
            virtual = VirtualNetwork.create_random_nw(v)

        # ILP solver
        prob = EmbedILP(virtual, physical)

        for solver_name in solvers_ilp:

            time_solution, status = prob.solve(
                solver_name=solver_name, timelimit=timelimit
            )

            if SolutionStatus[status] != "Solved":
                res_experiments["time"][solver_name][v] = time_solution
                res_experiments["value"][solver_name][v] = prob.current_val
            else:
                res_experiments["time"][solver_name][v] = time_solution
                res_experiments["value"][solver_name][v] = prob.solution.n_machines_used

        # Heuristic approaches
        for heu in solvers_heu:
            prob = solvers_heu[heu](virtual, physical)
            time_solution, status = prob.solve()

            if SolutionStatus[status] == "Not Solved":
                sys.exit("Failed to solve")
            elif SolutionStatus[status] == "Unfeasible":
                sys.exit("unfeasible Problem")
            else:
                pass

            res_experiments["time"][heu][v] = time_solution
            res_experiments["value"][heu][v] = prob.solution.n_machines_used

        pprint.pprint(res_experiments)


        with open(
            os.path.join("results", f"res_{net_type}_{timelimit}s.pickle"), "wb"
        ) as res_file:
            pickle.dump(res_experiments, res_file, protocol=pickle.HIGHEST_PROTOCOL)


if __name__ == "__main__":
    os.makedirs(os.path.join(os.path.dirname(__file__), "results"), exist_ok=True)
    time_comparison_grid5000(timelimit=120, net_type="fat-tree")
    time_comparison_grid5000(timelimit=120, net_type="random")
