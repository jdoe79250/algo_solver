import itertools
import os
import pickle

import matplotlib.pyplot as plt

plt.rc("text", usetex=True)
plt.rc("font", family="serif")
plt.tight_layout()


def plot_grid5000(filename, nw_type="ft"):
    markers = itertools.cycle(("x", "^", "+", ".", "o", "*"))
    colors = itertools.cycle(["r", "g", "k", "b", "orange", "m", "y"])
    linestyles = itertools.cycle(["-", "--", "-.", ":"])

    with open(os.path.join("results", filename), "rb") as pickle_file:
        res = pickle.load(pickle_file)
    print(res)

    x_vals = res["x"]

    fig, (ax0, ax1) = plt.subplots(1, 2, figsize=(10, 3))

    for algo in res["time"]:
        mkr = next(markers)
        col = next(colors)
        lns = next(linestyles)
        x_to_consider = [x for x in x_vals if res["value"][algo][x] != 0]
        y_to_consider = [y for y in res["value"][algo].values() if y != 0]

        ax0.plot(
            x_vals,
            list(res["time"][algo].values()),
            c=col,
            linewidth=3,
            linestyle=lns,
            markersize=6,
            marker=mkr,
            label=algo if algo != "cplex" else "ILP",
            alpha=0.7,
        )
        ax1.plot(
            x_to_consider,
            y_to_consider,
            c=col,
            linewidth=3,
            markersize=6,
            linestyle=lns,
            marker=mkr,
            label=algo if algo != "cplex" else "ILP",
            alpha=0.7,
        )

    ax0.set_xlim(min(x_vals), max(x_vals) + 0.1)
    ax0.set_yscale("log")
    if "random" in nw_type:
        ax0.set_xlabel(r"\textbf{Number of Nodes}", fontsize=13)
        ax1.set_xlabel(r"\textbf{Number of Nodes}", fontsize=13)
        # plt.suptitle(r'\textbf{Random}', fontsize=14)
    else:
        ax0.set_xlabel(r"\textbf{k}", fontsize=13)
        ax1.set_xlabel(r"\textbf{k}", fontsize=13)
        # plt.suptitle(r'\textbf{Fat Tree}', fontsize=14)

    ax0.set_ylabel(r"\textbf{Time (s)}", fontsize=13)

    ax1.legend(loc="upper left", ncol=2)
    ax0.grid(True)

    ax1.set_xlim(min(x_vals), max(x_vals))
    ax1.set_ylim(0, 70)
    ax1.set_ylabel(r"\textbf{Number of Physical Hosts}", fontsize=13)

    ax1.grid(True)

    plt.savefig(f"plots/{nw_type}.pdf", bbox_inches="tight")


if __name__ == "__main__":

    plot_grid5000("res_fat-tree_120s.pickle", "res_fat-tree_120s")
    plot_grid5000("res_random_120s.pickle", "res_random_120s")
