from util import *
from tqdm import tqdm
from config import Config as config
from dataset import TrajectoryDataset

if __name__ == '__main__':
    datasets = TrajectoryDataset('./data/eth', config.max_seqlen, config)
    for idx,batch in tqdm(enumerate(datasets)):
        print(idx, '-', batch)
