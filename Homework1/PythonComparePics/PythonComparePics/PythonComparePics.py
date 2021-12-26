import cv2
import numpy as np
from PIL import Image
import requests
from io import BytesIO
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import difflib
import json
import flask
from flask import jsonify, request

def aHash(img):
    # aHash 計算
    img = cv2.resize(img, (8, 8)) # 調整成8*8大小
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) # 轉成灰階
    
    s = 0 # s為每個像素的和
    hash_str = '' # hash_str 是 hash 字串
    
    # 計算每個像素的和
    for i in range(8):
        for j in range(8):
            s = s+gray[i, j]

    avg = s/64 # 計算平均灰階值

    # 灰階 > 平均值時設定為 1，反之為 0，產生整張圖的 hash 字串
    for i in range(8):
        for j in range(8):
            if gray[i, j] > avg:
                hash_str = hash_str+'1'
            else:
                hash_str = hash_str+'0'
    return hash_str

def dHash(img):
    # dHash 計算
    img = cv2.resize(img, (9, 8)) # 調整成8*8大小

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) # 轉成灰階

    hash_str = ''

    # 每行前一個像素的灰階值大於後面像素的灰階值，則為1，反之為0
    for i in range(8):
        for j in range(8):
            if gray[i, j] > gray[i, j+1]:
                hash_str = hash_str+'1'
            else:
                hash_str = hash_str+'0'
    return hash_str

def pHash(img):
    # pHash

    img = cv2.resize(img, (32, 32)) # 調整成32*32大小

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) # 轉成灰階

    # 把灰階轉成float，並做 dct
    dct = cv2.dct(np.float32(gray))
    dct_roi = dct[0:8, 0:8]

    hash = []
    avreage = np.mean(dct_roi)
    for i in range(dct_roi.shape[0]):
        for j in range(dct_roi.shape[1]):
            if dct_roi[i, j] > avreage:
                hash.append(1)
            else:
                hash.append(0)
    return hash

def calculate(image1, image2):
    # 灰階直方图計算
    # Single Channel的直方圖相似度
    hist1 = cv2.calcHist([image1], [0], None, [256], [0.0, 255.0])
    hist2 = cv2.calcHist([image2], [0], None, [256], [0.0, 255.0])

    # 計算直方圖的重合度
    degree = 0
    for i in range(len(hist1)):
        if hist1[i] != hist2[i]:
            degree = degree + \
                (1 - abs(hist1[i] - hist2[i]) / max(hist1[i], hist2[i]))
        else:
            degree = degree + 1
    degree = degree / len(hist1)
    return degree

def classify_hist_with_split(image1, image2, size=(256, 256)):
    # RGB 3 個 Channel 的直方圖相似度
    # resize 之後，切成 RGB 3 通道，個別計算直方圖的相似值
    image1 = cv2.resize(image1, size)
    image2 = cv2.resize(image2, size)
    sub_image1 = cv2.split(image1)
    sub_image2 = cv2.split(image2)
    sub_data = 0
    for im1, im2 in zip(sub_image1, sub_image2):
        sub_data += calculate(im1, im2)
    sub_data = sub_data / 3

    return sub_data

def cmpHash(hash1, hash2):
    # Hash值比對
    # 1和0的順序就等於圖片的特徵hash字串。
    # 顺序不固定，但是比對的時候必需是相同的顺序。
    # 比對兩張圖片的hash字串，計算Hamming distance，不同的位數越小表示圖片越相似
    n = 0

    if len(hash1) != len(hash2):
        return -1

    # 比對每個 hash 字串的字元
    for i in range(len(hash1)):
        if hash1[i] != hash2[i]: # 不相等則n++
            n = n + 1
        return n

def bytes_to_cvimage(filebytes):
    # 圖片的 byte stream 轉成 cv image
    image = Image.open(filebytes)
    img = cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2BGR)
    return img

def runAllImageSimilaryFun(para1, para2):
    # aHash、dHash、pHash算法，值越小越相似，完全相同的話就是0
    # 3 Channel 與 Single Channel直方圖的值是 0-1之間，值越大越相似，完全相同的話就是1

    # 讀 local image file
    img1 = cv2.imread(para1)
    img2 = cv2.imread(para2)

    hash1 = aHash(img1)
    hash2 = aHash(img2)
    n1 = cmpHash(hash1, hash2)
    print('aHash：', n1)

    hash1 = dHash(img1)
    hash2 = dHash(img2)
    n2 = cmpHash(hash1, hash2)
    print('dHash：', n2)

    hash1 = pHash(img1)
    hash2 = pHash(img2)
    n3 = cmpHash(hash1, hash2)
    print('pHash：', n3)

    n4 = classify_hist_with_split(img1, img2)

    print('3 Channel 直方圖算法相似度：', n4)

    n5 = calculate(img1, img2)
    print("Single channel 的直方圖", n5)

    #這幾行是因為 n4/n5 會有純數值的狀況，所以沒辦法用 index 取值!!!!!!    
    n4Ratio = n4

    if not isinstance(n4, float):
        n4Ratio = n4[0]

    n5Ratio = n5

    if not isinstance(n5, float):
        n5Ratio = n5[0]

    print("%d %d %d %.2f %.2f " % (n1, n2, n3, round(n4Ratio, 2), n5Ratio))
    print("%.2f %.2f %.2f %.2f %.2f " % (1-float(n1/64), 1 -
                                         float(n2/64), 1-float(n3/64), round(n4Ratio, 2), n5Ratio))

    result = [{'n1': n1, 'n2': n2, 'n3': n3, 'n4': str(round(n4Ratio, 2)), 'n5': str(n5Ratio)}]
    return json.dumps(result) #回傳 JSON 格式的結果

    #plt.subplot(121)
    #plt.imshow(Image.fromarray(cv2.cvtColor(img1, cv2.COLOR_BGR2RGB)))
    #plt.subplot(122)
    #plt.imshow(Image.fromarray(cv2.cvtColor(img2, cv2.COLOR_BGR2RGB)))
    #plt.show()

#if __name__ == "__main__":
#    #p1="https://ww3.sinaimg.cn/bmiddle/007INInDly1g336j2zziwj30su0g848w.jpg"
#    #p2="https://ww2.sinaimg.cn/bmiddle/007INInDly1g336j10d32j30vd0hnam6.jpg"
#    p1="C:/Users/user/Desktop/NCKU_110_CBIR/photoset/_query/quert_ponda.jpg"
#    #p2="C:/Users/user/Desktop/NCKU_110_CBIR/photoset/panda/panda_02.jpg"
#    p2="C:/Users/user/Desktop/NCKU_110_CBIR/photoset/statue of liberty/liberty_01.jpg"
#    #p2="C:/Users/user/Desktop/NCKU_110_CBIR/photoset/strawberry/strawberry_12.jpg"
#    runAllImageSimilaryFun(p1,p2)

app = flask.Flask(__name__)

@app.route('/ComparePics', methods=['GET'])
def ComparePics():
    if 'p1' in request.args and 'p2' in request.args:
        return runAllImageSimilaryFun(request.args['p1'], request.args['p2'])
    else:
        return 'Error: No p1 & p2 provided. Please specify 2 pics.'

app.run()