# Python script to run all modules in one go, without generating intermediate files.
import pickle as pickle

from base import *
from distance import *
from greedy import *
from ioUtils import *
from scipy import io


def pathlet_dict_to_array(pathlet_dict):
    """
    clusters = [cluster1, cluster2, cluster3, ...],
    cluster=[subtrajectory1, subtrajectory2, ...],
    subtrajectory = [point1, point2, ...],
    point=[lat, lng]
    """

    clusters = []
    pathlets = []

    for pathlet, subtrajs in pathlet_dict.items():

        pth = []
        trajID = pathlet.trajID
        start, end = pathlet.bounds
        apts = trajs[trajID].pts[start : end + 1]
        for point in apts:
            pth.append([point.lon, point.lat])
        pathlets.append(np.array(pth))

        cluster = []

        for subtraj in subtrajs:
            subtrajectory = []

            trajID = subtraj.trajID
            start, end = subtraj.bounds

            pts = trajs[trajID].pts[start : end + 1]
            for point in pts:
                subtrajectory.append([point.lon, point.lat])

            cluster.append(np.array(subtrajectory))
        clusters.append(np.array(cluster))
    return pathlets, clusters


def save_result(fname, pathlets, clusters):
    path = "./result/" + fname
    io.savemat(path, {"pathlets": pathlets, "clusters": clusters})


if __name__ == "__main__":
    # if len(sys.argv) != 7:
    #    print "Wrong command. Correct command is python allInOne.py fileName rmin rmax c1 c2 c3."

    print("Loading trajectories ...")
    trajs = readTrajsFromTxtFile("data/TRAFFIC.txt")

    # 核心参数，表示Frechet距离的上下届，从迭代中从rmin开始，每次循环后翻倍，最大至rmax
    rmin, rmax = 1, 8

    print("Computing Frechet distances ...")
    distPairs1 = process(trajs, rmin, rmax)

    # distPairs1 is of form {(pth, straj):dist}, change it to distPairs2 of the form {(pth, trajID):[(straj, dist)]}
    distPairs2 = {}
    for k, v in distPairs1.items():
        pth, trID, dist, straj = k[0], k[1].trajID, v, k[1]
        if (pth, trID) in distPairs2:
            distPairs2[(pth, trID)].append((straj, dist))
        else:
            distPairs2[(pth, trID)] = [(straj, dist)]

    print("Computing prerequisite data structures ...")
    (strajCov, ptStraj, strajPth, trajCov) = preprocessGreedy(trajs, distPairs2)

    c1, c2, c3 = 1, 1, 1

    print("Running greedy algorithm ...")
    retVal = runGreedy(
        trajs, distPairs2, strajCov, ptStraj, strajPth, trajCov, c1, c2, c3
    )

    # 保存运算结果
    pathlets, clusters = pathlet_dict_to_array(retVal[0])
    save_result(
        f"result_rmin{rmin}_rmax{rmax}_c{c1}_{c2}_{c3}.mat",
        pathlets=pathlets,
        clusters=clusters,
    )

    # 数据读取
    # data_mat = io.loadmat(f"./result/result_rmin{rmin}_rmax{rmax}_c{c1}_{c2}_{c3}.mat")
    # pathlets_data = data_mat["pathlets"]
    # clusters_data = data_mat["clusters"]
    # 注：clusters_data 为 pathlets_data 相对应的聚类
    # clusters_data = [cluster1, cluster2, cluster3, ...],
    # cluster = ([subtrajectory1, subtrajectory2, ...],)
    # subtrajectory = ([point1, point2, ...],)
    # point = [lat, lng]
