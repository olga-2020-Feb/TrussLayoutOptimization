from matplotlib import pyplot as plt


def mathplotlibPlot(Cn, Nd, a, q, str, threshold, update):
    plt.ion() if update else plt.ioff()
    plt.clf()
    plt.axis('off')
    plt.axis('equal')
    plt.draw()
    plt.title(str)
    tk = 5 / max(a)
    for i in [i for i in range(len(a)) if a[i] >= threshold]:
        if all([q[lc][i] >= 0 for lc in range(len(q))]):
            c = 'r'
        elif all([q[lc][i] <= 0 for lc in range(len(q))]):
            c = 'b'
        else:
            c = 'tab:gray'
        pos = Nd[Cn[i, [0, 1]].astype(int), :]
        plt.plot(pos[:, 0], pos[:, 1], c, linewidth=a[i] * tk)
    plt.pause(0.01) if update else plt.show()