""" DBSCAN

    Density-Based Spatial Clustering of Applications with Noise.
"""

import os
import sys
import numpy as np
import platform
import matplotlib
if platform.system() is "Windows":
    import matplotlib.pyplot as plt
else:
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt


def DBSCAN(x, y, r0, MinPts, Lx, Ly, cell_list):
    n = x.size
    visited = np.zeros(n, bool)
    clustered = np.zeros(n, bool)
    c = []
    for i in range(x.size):
        if visited[i]:
            continue
        visited[i] = True
        neighborPts = region_query(i, x, y, r0, Lx, Ly, cell_list)
        if len(neighborPts) < MinPts:
            pass
        else:
            c_new = expand_cluster(i, neighborPts, visited, clustered, x, y,
                                   r0, MinPts, Lx, Ly, cell_list)
            c.append(c_new)
    return c


def expand_cluster(i, neighborPts, visited, clustered, x, y, r0, MinPts, Lx,
                   Ly, cell_list):
    c_new = [i]
    clustered[i] = True
    j = 0
    while j < len(neighborPts):
        k = neighborPts[j]
        if not visited[k]:
            visited[k] = True
            neighborPts_new = region_query(k, x, y, r0, Lx, Ly, cell_list)
            if len(neighborPts_new) >= MinPts:
                neighborPts.extend(neighborPts_new)
        if not clustered[k]:
            clustered[k] = True
            c_new.append(k)
        j += 1
    return c_new


def region_query(i, x, y, r0, Lx, Ly, cell_list):
    def cal_dis(i, j):
        dx = x[j] - x0
        dy = y[j] - y0
        if dx < -0.5 * Lx:
            dx += Lx
        elif dx > 0.5 * Lx:
            dx -= Lx
        if dy < -0.5 * Ly:
            dy += Ly
        elif dy > 0.5 * Ly:
            dy -= Ly
        return dx**2 + dy**2

    neighbor = []
    x0 = x[i]
    y0 = y[i]
    col0 = int(x0)
    row0 = int(y0)
    for row in range(row0 - 1, row0 + 2):
        if row < 0:
            row += Ly
        elif row >= Ly:
            row -= Ly
        for col in range(col0 - 1, col0 + 2):
            if col < 0:
                col += Lx
            elif col >= Lx:
                col -= Lx
            if cell_list[row, col] is not 0:
                for j in cell_list[row, col]:
                    if j != i and cal_dis(i, j) < r0:
                        neighbor.append(j)
    return neighbor


def create_cell_list(x, y, Lx, Ly):
    cell = np.zeros((Ly, Lx), list)
    n = x.size
    for i in range(n):
        col = int(x[i])
        row = int(y[i])
        if col >= Lx:
            col = Lx - 1
        if row >= Ly:
            row = Ly - 1
        if cell[row, col] == 0:
            cell[row, col] = [i]
        else:
            cell[row, col].append(i)
    return cell


def cal_cluster_dis(x, y, Lx, Ly, ns_dict, MinPts=3):
    """ Issue: normalization
    """
    N = Lx * Ly
    cell_list = create_cell_list(x, y, Lx, Ly)
    cluster = DBSCAN(x, y, 1, MinPts, Lx, Ly, cell_list)
    mass = [len(c) for c in cluster]
    for n in mass:
        if n in ns_dict:
            ns_dict[n] += 1/N
        else:
            ns_dict[n] = 1/N
    ns1 = (Lx*Ly - sum(mass)) / N
    if 1 in ns_dict:
        ns_dict[1] += ns1
    else:
        ns_dict[1] = ns1


def mean_ns(file, t_beg=300, t_end=None, dt=1, out=False):
    para_list = file.split("_")
    Lx = int(para_list[3])
    Ly = int(para_list[4])
    eps = float(para_list[2])
    snap = load_snap.RawSnap(file)
    ns_dict = {}
    count = 0
    for frame in snap.gene_frames(t_beg, t_end, dt):
        x, y, theta = frame
        cal_cluster_dis(x, y, Lx, Ly, ns_dict, MinPts=1)
        count += 1
    for key in ns_dict:
        ns_dict[key] /= count
    if not out:
        s = []
        ns = []
        for key in ns_dict:
            ns.append(ns_dict[key])
            s.append(key)
        return s, ns
    else:
        with open(r"ns_%d_%d_%g.dat" % (Lx, Ly, eps), "w") as f:
            for key in sorted(ns_dict.keys()):
                f.write("%d\t%f\n" % (key, ns_dict[key]))


def show_cluster(x, y, Lx, Ly, ax=None, c=None, MinPts=3):
    if c is None:
        cell_list = create_cell_list(x, y, Lx, Ly)
        c = DBSCAN(x, y, 1, MinPts, Lx, Ly, cell_list)
    c = sorted(c, key=lambda x: len(x), reverse=True)
    if ax is None:
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(14, 3.5))
        flag_show = True
    else:
        flag_show = False
    clist = plt.cm.jet(np.linspace(1, 0, 20))
    for i, ci in enumerate(c):
        if i < 20:
            color = clist[i]
        else:
            color = "#7f7f7f"
        ax.plot(y[ci], x[ci], "o", c=color, ms=0.2)
    ax.set_xlim(0, Ly)
    ax.set_ylim(0, Lx)
    ax.set_xlabel("$y$")
    ax.set_ylabel("$x$")
    ax.set_title(r"$\eta=0.18, \epsilon=0, \rho_0=1, L_x=%d, L_y=%d$" %
                 (Lx, Ly))
    if flag_show:
        plt.tight_layout()
        plt.show()
        # plt.savefig("cluster_%d_%d.jpg" % (Lx, Ly), dpi=200)
        plt.close()


if __name__ == "__main__":
    import load_snap

    if platform.system() is not "Windows":
        path, file = sys.argv[1].split("/")
        os.chdir(path)
        mean_ns(file, t_beg=300, out=True)
    else:
        os.chdir(r"D:\tmp")
        file1 = r"so_0.35_0.02_220_800_176000_2000_1234.bin"
        mean_ns(file1, t_beg=300, t_end=301, out=True)

