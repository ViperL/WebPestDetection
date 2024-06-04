import torch.nn as nn

from nets.classifier import Resnet50RoIHead, VGG16RoIHead
from nets.resnet50 import resnet50
from nets.rpn import RegionProposalNetwork
from nets.vgg16 import decom_vgg16
from torchvision import transforms

import time
import numpy as np
import matplotlib.pyplot as plt
def feature_imshow(inp):
    inp = inp.cpu()
    if(inp.shape[3]>7):
        print(inp.shape)
        inp=inp.squeeze(0)
        plt.figure(figsize=(12, 7))
        shape_2=inp.shape[0]
        step = int(shape_2/20)
        plt.title(str(shape_2))
        for i in range(20):
            plt.subplot(4, 5, i+1)
            plt.axis('off')     #去掉坐标系
            #plt.title(str(i*step))
            plt.imshow(transforms.ToPILImage()(inp[i*step]))
            i+=1
        plt.savefig("map_out/vision/{}-{}.png".format(str(time.time()),shape_2))
    #plt.pause(0.001)

class FasterRCNN(nn.Module):
    def __init__(self,  num_classes,  
                    mode = "training",
                    feat_stride = 16,
                    anchor_scales = [8, 16, 32],
                    ratios = [0.5, 1, 2],
                    backbone = 'vgg',
                    pretrained = False):
        super(FasterRCNN, self).__init__()
        self.feat_stride = feat_stride
        #---------------------------------#
        #   一共存在两个主干
        #   vgg和resnet50
        #---------------------------------#
        if backbone == 'vgg':
            self.extractor, classifier = decom_vgg16(pretrained)
            #---------------------------------#
            #   构建建议框网络
            #---------------------------------#
            self.rpn = RegionProposalNetwork(
                512, 512,
                ratios          = ratios,
                anchor_scales   = anchor_scales,
                feat_stride     = self.feat_stride,
                mode            = mode
            )
            #---------------------------------#
            #   构建分类器网络
            #---------------------------------#
            self.head = VGG16RoIHead(
                n_class         = num_classes + 1,
                roi_size        = 7,
                spatial_scale   = 1,
                classifier      = classifier
            )
        elif backbone == 'resnet50':
            self.extractor, classifier = resnet50(pretrained)
            #---------------------------------#
            #   构建classifier网络
            #---------------------------------#
            self.rpn = RegionProposalNetwork(
                1024, 512,
                ratios          = ratios,
                anchor_scales   = anchor_scales,
                feat_stride     = self.feat_stride,
                mode            = mode
            )
            #---------------------------------#
            #   构建classifier网络
            #---------------------------------#
            self.head = Resnet50RoIHead(
                n_class         = num_classes + 1,
                roi_size        = 14,
                spatial_scale   = 1,
                classifier      = classifier
            )
            
    def forward(self, x, scale=1.):
        #---------------------------------#
        #   计算输入图片的大小
        #---------------------------------#
        img_size        = x.shape[2:]
        #---------------------------------#
        #   利用主干网络提取特征
        #---------------------------------#
        base_feature    = self.extractor.forward(x)
        #feature=x.detach()
        #feature_imshow(feature)
        #---------------------------------#
        #   获得建议框
        #---------------------------------#
        _, _, rois, roi_indices, _  = self.rpn.forward(base_feature, img_size, scale)
        #---------------------------------------#
        #   获得classifier的分类结果和回归结果
        #---------------------------------------#
        roi_cls_locs, roi_scores    = self.head.forward(base_feature, rois, roi_indices, img_size)
        return roi_cls_locs, roi_scores, rois, roi_indices

    def freeze_bn(self):
        for m in self.modules():
            if isinstance(m, nn.BatchNorm2d):
                m.eval()
