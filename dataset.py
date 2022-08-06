# 准备数据,参考social-stgcnn和trAISformer
import os
from tqdm import tqdm
from util import *
from torch.utils.data import Dataset


class TrajectoryDataset(Dataset):
    """customized pytorch dataset"""

    def __init__(self, data_dir, seq_len, max_seqlen=96) -> None:
        super(TrajectoryDataset).__init__()
        # TODO 不知道有没有问题!
        r"""
        Args:
            data_dir::=要读入的已经格式化好了的文件
                <timestep> <ped_id> <x> <y>
            max_seqlen:transformer一个seq的最大长度
                    
        Returns:
            seq: Tensor of (max_seqlen, [lat,lon,sog,cog]).
            mask: Tensor of (max_seqlen, 1). mask[i] = 0.0 if x[i] is a
            padding.
            seqlen: sequence length.
            mmsi: vessel's MMSI.
            time_start: timestamp of the starting time of the trajectory.
        """
        self.data_dir = data_dir
        self.max_seqlen = max_seqlen
        self.seq_len = seq_len
        # self.data 存储DataFrame对象,一个DataFrame对象表示一个小整体?
        self.data = {'frame_ships': [], 'trajectories': []}
        # self.sample_data存放一段一段序列开头的帧id信息
        self.sample_data = np.array([[], []])
        # 读取根目录下的所有文件作为测试集或者训练集(如一个eth文件夹为一个整体)
        for seti, path in enumerate(os.listdir(data_dir)):
            print('开始读取{}数据'.format(path))
            # 一个path表示一个独立的整体(但仍然有很多文件)
            path = os.path.join(data_dir, path)
            data = read_epoch(path)

            # 提取帧号
            frames_id = np.unique(data.loc[:, ('timestep')]).tolist()
            # 提取船的mmsi(id)号
            mmsi_list = np.unique(data.loc[:, ('mmsi')]).tolist()
            # 生成每搜船的轨迹信息——时间信息
            trajectories = []
            frame_ships = []
            for _, ship_id in tqdm(enumerate(mmsi_list)):
                # trajectory存放每个人的轨迹信息——时间信息
                trajectory = data[data.loc[:, ('mmsi')] == ship_id]
                # 过短，抛弃(但是不会出现这个情况,以为在预处理时已经抛弃了)
                if len(trajectory) < 2:
                    continue
                # 保存轨迹
                trajectories.append(trajectory)

            self.data['trajectories'].append(trajectories)

            # 生成每一帧的行人信息——空间信息
            for _, frame_id in tqdm(enumerate(frames_id)):
                # frame_ship存放id为frame_id的帧的所有行人信息
                frame_ship = data[data.loc[:, ('timestep')] == frame_id]
                frame_ship.reset_index(drop=True, inplace=True)  # 重新排序标号

                # 保存framed_id帧的信息(frame_ship[i]表示i帧的船信息)
                frame_ships.append(frame_ship)

            self.data['frame_ships'].append(frame_ships)
            print('读取{}数据完成'.format(path))
            print('开始准备item数据')

            set_id = []  # 保存frame_id_in_set元素对应的集合的id(即文件对应的id)
            # 保存所有能构成训练序列的帧首(长度即为样本的长度)包含所有文件的——即为了生成start和end
            frame_id_in_set = []
            frames_id = sorted(
                [frame_ship.loc[0, 'timestep'] for frame_ship in frame_ships])
            # 这里减去seq_length是为了防止最后的序列没办法凑成一个完整的预测序列
            maxframe = max(frame_ship) - self.seq_len
            frames_id = [x for x in frame_id
                         if not x > maxframe]  #提取出能构成完整序列的帧
            set_id.extend(list(seti for _ in range(len(frame_ship))))
            frame_id_in_set.extend(
                list(frame_ship[i] for i in range(len(frame_ship))))

            self.data_index = np.concatenate([
                self.data_index,
                np.concatenate([
                    np.array([frame_id_in_set], dtype=int),
                    np.array([set_id], dtype=int)
                ], 0)
            ], 1)

    def __getitem__(self, index):
        """Gets items.
        
        Returns:
            seq: Tensor of (max_seqlen, [lat,lon,sog,cog]).
            mask: Tensor of (max_seqlen, 1). mask[i] = 0.0 if x[i] is a padding.
            seqlen: sequence length.
            mmsi: vessel's MMSI.
            time_start: timestamp of the starting time of the trajectory.
        """
        seq = self.__get_seq(index)
        mask = self.__get_mask(index)
        seqlen = self.__get_seqlen(index)
        mmsi = self.__get_mmsi(index)

    def __get_seq(self, index):
        pass

    def __get_mask(self, index):
        pass

    def __get_seqlen(index):
        pass

    def __get_mmsi(index):
        pass
