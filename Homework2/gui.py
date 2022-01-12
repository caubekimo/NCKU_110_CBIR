import numpy as np
import tkinter as tk
from tkinter import filedialog
from tkinter import *
from PIL import ImageTk, Image

import numpy
#load the trained model to classify sign
from keras.models import load_model
model = load_model('traffic_classifier.h5')

#dictionary to label all traffic signs class.
classes = { 1:'速度限制 (20km/h)',
            2:'速度限制 (30km/h)', 
            3:'速度限制 (50km/h)', 
            4:'速度限制 (60km/h)', 
            5:'速度限制 (70km/h)', 
            6:'速度限制 (80km/h)', 
            7:'速限解除 (80km/h)', 
            8:'速度限制 (100km/h)', 
            9:'速度限制 (120km/h)', 
            10:'禁止超車', 
            11:'3.5 噸以上車輛禁止超車', 
            12:'優先行駛(下一個路口有優先行駛權)', 
            13:'幹道先行', 
            14:'讓路', 
            15:'停止', 
            16:'道路封閉', 
            17:'3.5 噸以上車輛禁止進入', 
            18:'禁止所有車輛進入', 
            19:'危險', 
            20:'左彎', 
            21:'右彎', 
            22:'連續彎路先向左', 
            23:'道路顛簸', 
            24:'路面溼滑', 
            25:'右側車道縮減', 
            26:'道路施工', 
            27:'注意號誌', 
            28:'當心行人', 
            29:'當心兒童', 
            30:'當心腳踏車', 
            31:'當心路面結冰/積雪',
            32:'注意野生動物', 
            33:'取消車速與超車限制', 
            34:'前方車道僅准右轉', 
            35:'前方車道僅准左轉', 
            36:'前方車道僅准直行', 
            37:'前方車道僅准直行及右轉', 
            38:'前方車道僅准直行及左轉', 
            39:'靠右行駛', 
            40:'靠左行駛', 
            41:'圓環遵行方向', 
            42:'恢復車輛可超車', 
            43:'恢復 3.5 噸以上車輛可超車' }

#initialise GUI
top=tk.Tk()
top.geometry('800x600')
top.title('交通號誌辨識')
top.configure(background='#CDCDCD')

label=Label(top,background='#CDCDCD', font=('arial',15,'bold'))
sign_image = Label(top)

def classify(file_path):
    global label_packed
    image = Image.open(file_path)
    image = image.resize((30,30))
    image = numpy.expand_dims(image, axis=0)
    image = numpy.array(image)
    # pred = model.predict_classes([image])[0]
    predict_x=model.predict([image]) 
    pred=np.argmax(predict_x,axis=1)[0]
    sign = classes[pred+1]
    print(sign)
    label.configure(foreground='#011638', text=sign) 

def show_classify_button(file_path):
    classify_b=Button(top,text="辨識",command=lambda: classify(file_path),padx=25,pady=25)
    classify_b.configure(background='#364156', foreground='white',font=('arial',16,'bold'))
    classify_b.place(relx=0.79,rely=0.46)

def upload_image():
    try:
        file_path=filedialog.askopenfilename()
        uploaded=Image.open(file_path)
        uploaded.thumbnail(((top.winfo_width()/2.25),(top.winfo_height()/2.25)))
        uploaded = uploaded.resize((350, 350))
        im=ImageTk.PhotoImage(uploaded)

        sign_image.configure(image=im)
        sign_image.image=im
        label.configure(text='')
        show_classify_button(file_path)
    except:
        pass

upload=Button(top,text="選擇圖片",command=upload_image,padx=150,pady=10)
upload.configure(background='#364156', foreground='white',font=('arial',16,'bold'))

upload.pack(side=BOTTOM,pady=50)
sign_image.pack(side=BOTTOM,expand=True)
label.pack(side=BOTTOM,expand=True)
heading = Label(top, text="交通號誌辨識",pady=20, font=('arial',20,'bold'))
heading.configure(background='#CDCDCD',foreground='#364156')
heading.pack()
top.mainloop()
