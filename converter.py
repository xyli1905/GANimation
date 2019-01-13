import os
import argparse
import glob
import torchvision.transforms as transforms
from torch.autograd import Variable
import torch
import cv2
import numpy as np
from options.test_options import TestOptions
from networks import generatorFoward
import utils.util as util
import pickle
import time
import random

class feedFoward:
    def __init__(self, path):
        self._model = generatorFoward.generatorFoward(conv_dim=64, c_dim=17, repeat_num=6)
        self._model.load_state_dict(torch.load(path))
        self._model.eval()
        self._transform = transforms.Compose([transforms.ToTensor(),
                                              transforms.Normalize(mean=[0.5, 0.5, 0.5],
                                                                   std=[0.5, 0.5, 0.5])
                                              ])

    def convert(self, face, desired_expression):
        face = torch.unsqueeze(self._transform(face), 0).float()
        desired_expression = torch.unsqueeze(torch.from_numpy(desired_expression/5.0), 0).float()
        start = time.clock()
        color, mask = self._model.forward(face, desired_expression)
        end = time.clock()
        print('forward time : ', end - start)
        # torch.onnx.export(self._model,(face, desired_expression), "alexnet.onnx", verbose=True)
        masked_result = mask * face + (1.0 - mask) * color

        img = self.convertToimg(masked_result)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        return img
    
    def convertToimg(self, tensor):
        tensor = tensor.cpu().float()
        img = tensor.detach().numpy()[0]
        img = img*0.5+0.5
        img = np.transpose(img, (1, 2, 0))
        return img*254.0


def main():
    path = './checkpoints/refined_model/net_epoch_30_id_G.pth'
    convertor = feedFoward(path)
    # dummy_input = np.random.randint(255, size=(128, 128, 3)).astype(np.uint8)
    name = '202204'
    real_face_raw = cv2.imread('./sample_dataset/imgs/'+name+'.png')

    # real_face_raw = real_face_raw[15:203, 0:178]
    # real_face_raw = cv2.resize(real_face_raw,(128,128))

    real_face = cv2.cvtColor(real_face_raw, cv2.COLOR_BGR2RGB)
    expressions = np.ndarray((10,17), dtype = np.float)

    f = open('./sample_dataset/aus_openface.pkl', 'rb')
    conds = pickle.load(f)


    '''
    expressions[0] = np.array([0, 0, 0, 0, 2.5, 0, 0, 0, 5, 0, 0, 0, 0, 5, 0, 0, 0], dtype = np.float) # happy
    expressions[1] = np.array([3, 0, 5, 0, 2.5, 0, 0, 0, 0, 0, 5, 3.3, 0, 0, 0, 0, 0], dtype = np.float) # sad
    expressions[2] = np.array([0, 0, 5, 0, 0, 5, 0, 1.5, 0, 0, 0, 2.5, 0, 1.5, 0, 0, 0], dtype = np.float) # angry
    expressions[3] = np.array([5, 5, 0, 3.3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 5, 0, 0], dtype = np.float) # surprise
    '''
    a = np.array([0.25, 0.11, 0.2 , 0.16, 1.92, 1.03, 0.3 , 2.15, 2.88, 1.61, 0.03, 0.09, 0.16, 0.11, 2.25, 0.37, 0.05], dtype = np.float)
    # b = np.array([0.69, 0, 0.01 , 0, 0.19, 1.02, 0 , 0, 1.25, 1.41, 0, 0, 0.59, 0.05, 0.9, 0, 0.33], dtype = np.float)
    b = conds[name]/10
    c = (b - a)/9
    print(c)
    print('-------------------------')
    for i in range(10):
        # expressions[i] = np.array([0.25, 0.11, 0.2 , 0.16, 1.92, 1.03, 0.3 , 2.15, 2.88, 1.61, 0.03, 0.09, 0.16, 0.11, 2.25, 0.37, 0.05], dtype = np.float) + np.random.uniform(-0.1, 0.1, 17)
        # expressions[i] = np.array([0.69, 0, 0.01 , 0, 0.19, 1.02, 0 , 0, 1.25, 1.41, 0, 0, 0.59, 0.05, 0.9, 0, 0.33], dtype = np.float) + np.random.uniform(-0.1, 0.1, 17)
        expressions[i] = c * i + a
        print(expressions[i])

    # origin_expression = np.array([0, 0, 0.46, 0, 0, 0, 0.03, 0, 0, 0.59, 0.02, 0.22, 0, 0.21, 0, 0, 0], dtype = np.float)

    result = real_face_raw
    for exp in expressions:
        img = convertor.convert(real_face, exp)
        result = np.hstack((result, img))
    cv2.imshow('result', result/254.0)
    cv2.waitKey()



if __name__ == '__main__':
    main()