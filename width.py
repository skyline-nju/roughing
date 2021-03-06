import numpy as np
import os
import matplotlib.pyplot as plt
from scipy import stats
import order_para


def read(file, ncut=300):
    with open(file) as f:
        lines = f.readlines()[ncut:]
        n = len(lines)
        data = np.zeros((n, 7))
        for j, line in enumerate(lines):
            for i, s in enumerate(line.replace("\n", "").split("\t")):
                if s == "":
                    data[j, i] = -1
                else:
                    data[j, i] = float(s)
        return data


def filtering(t0, w0, max_dw=100):
    t = []
    w = []
    for i in range(t0.size):
        if len(t) > 0:
            if w0[i] - w[-1] < max_dw and w0[i] > 0:
                t.append(t0[i])
                w.append(w0[i])
        else:
            t.append(t0[i])
            w.append(w0[i])
    return np.array(t), np.array(w)


def phi_vs_w(m1, m2):
    xmin = m1.min()
    xmax = m1.max()
    ymin = m2.min()
    ymax = m2.max()

    X, Y = np.mgrid[xmin:xmax:100j, ymin:ymax:100j]
    values = np.vstack([m1, m2])
    kernel = stats.gaussian_kde(values)
    # Z = np.reshape(kernel(positions).T, X.shape)
    z = kernel(values).T
    print(z.shape)
    fig, ax = plt.subplots()
    sca = ax.scatter(m1, m2, s=1, c=z, cmap="jet")
    ax.set_xlim([xmin, xmax])
    ax.set_ylim([ymin, ymax])
    plt.colorbar(sca)
    plt.show()
    plt.close()


if __name__ == "__main__":
    os.chdir(r"data")
    Lx = 220
    Lys = np.arange(100, 1100, 100)
    phi = np.zeros(Lys.size)
    w = np.zeros((Lys.size, 5))
    for i, Ly in enumerate(Lys):
        file = r"width\so_0.35_0_%d_%d_%d_2000_1234.dat" % (Lx, Ly, Lx * Ly)
        file2 = r"phi\p_0.35_0_1_%d_%d_1234.dat" % (Lx, Ly)
        data = read(file)
        line = "%d" % Ly
        phi[i] = np.mean(order_para.read(file2)[5000:])
        line += "\t%f" % (phi[i])
        t1, w1 = filtering(data[:, 0], data[:, 2])
        w[i, 0] = np.mean(w1)
        for j in range(5):
            tj, wj = filtering(data[:, 0], data[:, j+2])
            w[i, j] = np.mean(wj)
            line += "\t%f" % (w[i, j])
        print(line)
    plt.plot(Lys, w[:, 1:], "-o")
    plt.show()
    plt.close()
