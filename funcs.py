import math as m
import pandas as pd
import matplotlib.pyplot as plt


def euclid_dis(x1, y1, x2, y2):  #find the euclidean distance between two points
    return m.sqrt(m.pow(x1-x2, 2) + m.pow(y1-y2, 2))


def fnwd(x1, y1, d, df, vv, i):  #find number of neighbours with distance d from the point
    pts_check = 0  #number of neighbours for current point
    for j in range(df.shape[0]):
        if j == i:
            continue
        else:
            x2 = df.loc[j, 'x']
            y2 = df.loc[j, 'y']
            dis = euclid_dis(x1, y1, x2, y2)
            if dis <= d:
                #add to a virtual visited array provided by the dbs, now if the point is core then add all those points
                #to visited else continue
                vv.append(j)
                pts_check += 1

    return pts_check


def ckpfc(final_clusters, key, temp_cluster):  #check if key is present in the final cluster
    for i in range(len(final_clusters)):
        for j in range(len(final_clusters[i])):
            if key in temp_cluster[final_clusters[i][j]]:
                return i
    return -1


def plot_dbs(final_clusters, final_noise, df, temp_clusters, solution, minpts, eps):
    hex_colors = ['#5c3af2', '#cd8d05', '#71cc60', '#8f878c', '#9b3132', '#38f73b', '#57d0ec', '#e1b72d',
                  '#a2350c', '#068ac9', '#b015e5', '#f8d57f', '#a1dd38', '#5b5c8b', '#e9aa3f', '#7d2a8f', '#1bc13c',
                  '#753ee2', '#6cbbb4']

    fig, ax = plt.subplots()  # creating figure and axis objects

    for i in range(len(final_clusters)):
        x1 = df.loc[final_clusters[i][0], 'x']
        y1 = df.loc[final_clusters[i][0], 'y']
        plt.plot(x1, y1, 'o', color=hex_colors[i])
        for j in range(len(final_clusters[i])):
            for key in temp_clusters[final_clusters[i][j]]:
                x = df.loc[key, 'x']
                y = df.loc[key, 'y']
                plt.plot(x, y, 'o', color=hex_colors[i])

    for i in range(len(final_noise)):
        x = df.loc[final_noise[i], 'x']
        y = df.loc[final_noise[i], 'y']
        plt.plot(x, y, 'o', color="black")

    for key in solution:
        x = df.loc[key, 'x']
        y = df.loc[key, 'y']
        plt.plot(x, y, 'o', color="red")

    fig.suptitle(f"minpts = {minpts} , eps = {eps}")
    plt.show()


def fmid(dictionary):  #find max in a dictionary
    maxi = 0
    maxi_key = 0
    for key in dictionary:
        if dictionary[key] > maxi:
            maxi = dictionary[key]
            maxi_key = key
    return maxi_key


def ckptc(temp_clusters, target):  #check if key is present in temp_cluster
    temp_soln = list()
    for key in temp_clusters:
        if target in temp_clusters[key]:
            temp_soln.append(key)
    return temp_soln


def fsfc(final_clusters, temp_clusters):  #find solution to cluster
    fs = dict()
    for i in range(len(final_clusters)):
        solution = dict()
        for j in range(len(final_clusters[i])):
            soln = ckptc(temp_clusters, final_clusters[i][j])
            if len(soln) == 0:
                fs[final_clusters[i][j]] = 0
            else:
                for k in range(len(soln)):
                    if soln[k] in solution:
                        solution[soln[k]] += 1
                    else:
                        solution[soln[k]] = 1

        res = fmid(solution)
        try:
            fs[res] = solution[res]
        except KeyError:
            continue

    return fs


def dbs(eps, minpts, file):

    df = pd.read_csv(file)
    temp_clusters = dict()
    temp_temp_clusters = dict()
    temp_noise = list()

    #find all core points and temporary noise points
    for i in range(df.shape[0]):
        x1 = df.loc[i, 'x']
        y1 = df.loc[i, 'y']
        vv = list()
        pts = fnwd(x1, y1, eps, df, vv, i)
        temp_dict = dict()
        if pts >= minpts:
            for j in range(len(vv)):
                temp_dict[vv[j]] = True
            temp_clusters[i] = temp_dict
            temp_temp_clusters[i] = temp_dict
        else:
            temp_noise.append(i)

    #filter the noise
    final_noise = list()

    for i in range(len(temp_noise)):
        final_noise.append(temp_noise[i])

    for i in range(len(temp_noise)):
        for key in temp_clusters:
            if temp_noise[i] in temp_clusters[key]:
                try:
                    final_noise.remove(temp_noise[i])
                except ValueError:
                    continue

    final_clusters = list()

    while len(temp_temp_clusters) != 0:
        flag = 0
        for key in temp_temp_clusters:
            res = ckpfc(final_clusters, key, temp_clusters)
            if res != -1:
                final_clusters[res].append(key)
                del temp_temp_clusters[key]
                flag += 1
                break
        if flag == 0:
            temp_list = list()
            ele = list(temp_temp_clusters.keys())[0]
            temp_list.append(ele)
            final_clusters.append(temp_list)
            del temp_temp_clusters[ele]

    solution = fsfc(final_clusters, temp_clusters)
    print(f"Number of clusters = {len(final_clusters)}")
    print(final_clusters)
    count = 0
    for key in solution:
        print(f"\nThe solution for cluster-{count+1} is:")
        print(f"\t{df.loc[key, 'x']}")
        print(f"\t{df.loc[key, 'y']}")
        print(f"\tThe number of core points within this loi are {solution[key]}")
        count += 1

    plot_dbs(final_clusters, final_noise, df, temp_clusters, solution, minpts, eps)
