import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import warnings
import os
import random
warnings.filterwarnings('ignore')
import pandas as pd
def iou(box0, box1):
    r0 = box0[3] / 2
    s0 = box0[:3] - r0
    e0 = box0[:3] + r0

    r1 = box1[3] / 2
    s1 = box1[:3] - r1
    e1 = box1[:3] + r1

    overlap = []
    for i in range(len(s0)):
        overlap.append(max(0, min(e0[i], e1[i]) - max(s0[i], s1[i])))

    intersection = overlap[0] * overlap[1] * overlap[2]
    union = box0[3] * box0[3] * box0[3] + box1[3] * box1[3] * box1[3] - intersection
    return intersection / union


def nms(output, nms_th):
    if len(output) == 0:
        return output

    output = output[np.argsort(-output[:, 0])]
    bboxes = [output[0]]
    for i in np.arange(1, len(output)):
        bbox = output[i]
        flag = 1
        for j in range(len(bboxes)):
            temp=iou(bbox[1:5], bboxes[j][1:5])
            if iou(bbox[1:5], bboxes[j][1:5]) >= nms_th:
                flag = -1
                break
        if flag == 1:
            bboxes.append(bbox)
    bboxes = np.asarray(bboxes, np.float32)
    bboxes=bboxes[np.argsort(-bboxes[:,0])]
    return bboxes
def get_result(patient):
    result=[]
    pbb_path='./bbox_result/'+patient+'_pbb.npy'
    if not os.path.exists(pbb_path):
        return -1,result,-1,-1
    pbb = np.load(pbb_path)
    pbb = pbb[pbb[:,0]>-1]
    pbb = nms(pbb,0.05)#输出的第一个是label表明是否为正样本后面4列数据为bbox的值 z x y radius
    img_path='./lungSeg/' + patient + '_clean.npy'
    img = np.load(img_path)
    df=pd.read_csv('cls.csv')
    cls_result = df[df['id'] == int(patient)]
    prob=list(cls_result['cancer'])
    prob=prob[0]
    if prob < 0.5:
        kind = '良性'
    else:
        kind = '恶性'
    n=len(pbb)
    for i in range(n):
        temp=[]
        box = pbb[i].astype('int')[1:]
        ax = plt.subplot(1,1,1)
        plt.cla()
        plt.imshow(img[0,box[0]],'gray')
        plt.axis('off')
        rect = patches.Rectangle((box[2]-box[3],box[1]-box[3]),box[3]*2,box[3]*2,linewidth=2,edgecolor='red',facecolor='none')
        ax.add_patch(rect)
        pos=(box[2]+box[3],box[1]+box[3])
        text_pos=(box[2]+box[3]+40,box[1]+box[3]+50)
        #plt.annotate('result is {0}\n coord is{1}'.format(kind,(box[2],box[1],box[0])),xy=pos,xytext=text_pos,fontsize=8,arrowprops=dict(facecolor='white',shrink=0.05))
        plt.savefig('./static/result/result_'+patient+'_'+str(i)+'.png')
        temp.append(i+1)
        temp.append((box[2],box[1],box[0]))
        temp.append(box[3])
        result.append(temp)
    return n,result,kind,prob