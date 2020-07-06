from matplotlib import pyplot as plt


def plot_and_save(name):
    plt.clf()
    plt.figure(num=None, figsize=(10, 10))
    carac = eval(name)
    carac2 = eval(f"{name}2")
    carac3 = eval(f"{name}3")
    plt.boxplot([carac[x] for x in sorted(carac.keys())], labels=sorted(carac.keys()),
                positions=[3 * x + 0 for x in range(len(carac.keys()))],
                notch=True,
                meanline=True)
    plt.boxplot([carac2[x] for x in sorted(carac2.keys())],
                labels=list(map(lambda x: f"BSA-{x}", sorted(carac2.keys()))),
                positions=[3 * x + 2 for x in range(len(carac.keys()))],
                notch=True,
                meanline=True)
    plt.boxplot([carac3[x] for x in sorted(carac3.keys())],
                labels=list(map(lambda x: f"ins-{x}\nn={len(carac3[x])}", sorted(carac3.keys()))),
                positions=[3 * x + 1 for x in range(len(carac3.keys()))],
                notch=True,
                meanline=True)
    plt.savefig(f'timesby{name}.png')


def unsort(res, useBest=True):
    sizesI = {}
    layersI = {}
    procsI = {}
    for (g, t) in res:
        t = float(t)
        if useBest:
            if int(g[0]) == 100 and int(g[1]) == 34:
                proc = int(g[2])
                if proc in procsI:
                    procsI[proc].append(t)
                else:
                    procsI[proc] = [t]
            if int(g[0]) == 100 and int(g[2]) == 6:
                layer = int(g[1])
                if layer in layersI:
                    layersI[layer].append(t)
                else:
                    layersI[layer] = [t]
            if int(g[2]) == 6 and int(g[1]) >= 0.33 * int(g[0]):
                size = int(g[0])
                if size in sizesI:
                    sizesI[size].append(t)
                else:
                    sizesI[size] = [t]
        else:
            proc = int(g[2])
            if proc in procsI:
                procsI[proc].append(t)
            else:
                procsI[proc] = [t]
            layer = int(g[1])
            if layer in layersI:
                layersI[layer].append(t)
            else:
                layersI[layer] = [t]
            size = int(g[0])
            if size in sizesI:
                sizesI[size].append(t)
            else:
                sizesI[size] = [t]
    return sizesI, layersI, procsI


if __name__ == '__main__':

    myHeur = ['0', '0', '0', '1', '0', '0', '0']
    myHeur2 = myHeur[:-1] + [str(1 - int(myHeur[-1]))]
    myHeur3 = myHeur[:-2] + [str(1 - int(myHeur[-2]))] + [myHeur[-1]]

    res = []
    res2 = []
    res3 = []

    with open("ress.csv") as file:
        file.readline()
        for index, line in enumerate(file.readlines()):
            lineSplitted = (line[:-1].split(";")[1:])
            heur = lineSplitted[6:-2]
            if heur == myHeur:
                graph = [lineSplitted[0], lineSplitted[1], lineSplitted[5]]
                time = lineSplitted[-1]
                res += [[graph, time]]
            if heur == myHeur2:
                graph2 = [lineSplitted[0], lineSplitted[1], lineSplitted[5]]
                time2 = lineSplitted[-1]
                res2 += [[graph2, time2]]
            if heur == myHeur3:
                graph3 = [lineSplitted[0], lineSplitted[1], lineSplitted[5]]
                time3 = lineSplitted[-1]
                res3 += [[graph3, time3]]
            if index % 1000000 == 0:
                print(index)

        sizes, layers, procs = unsort(res, False)
        sizes2, layers2, procs2 = unsort(res2, False)
        sizes3, layers3, procs3 = unsort(res3, False)
        best_sizes, best_layers, best_procs = unsort(res, True)
        best_sizes2, best_layers2, best_procs2 = unsort(res2, True)
        best_sizes3, best_layers3, best_procs3 = unsort(res3, True)

        plot_and_save("sizes")
        plot_and_save("layers")
        plot_and_save("procs")
        plot_and_save("best_sizes")
        plot_and_save("best_layers")
        plot_and_save("best_procs")
        exit()
