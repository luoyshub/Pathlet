from ioUtils import *
from scipy import io


# 将 np.array 转换为字典
def convertArrayToDict(data):
    trajs = {}
    for trID in range(data.shape[0]):
        trajectary = traj()
        timestamp = 0
        for point in data[trID]:
            lat, lon = point
            trajectary.addPt(lat, lon, trID, timestamp)
            timestamp += 1
        trajs[trID] = trajectary
    return trajs


start_index = 145
end_index = 149
data_mat = io.loadmat("data/TRAFFIC_trans.mat")
data_ori = data_mat["data"]
data_subset = data_ori[start_index:end_index]
data_Dict = convertArrayToDict(data_subset)
writeTrajsToTxtFile(f".\data\TRAFFIC_subset_{start_index}_{end_index}.txt", data_Dict)
