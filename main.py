import numpy as np
import torch
import pynput

from grabscreen import grab_screen
from cs_model import load_model
import cv2
import win32gui
import win32con
import argparse

from mouse_controller import lock,recoil_control
from threading import Thread

import sys
sys.path.append("..")
from utils.general import non_max_suppression
from utils.datasets import letterbox
from utils.general import scale_coords,xyxy2xywh
from utils.plots import plot_one_box



x,y=(1920,1080)
re_x ,re_y =(1920,1080)
device ='cuda'
half =device!='cpu'
img_size =640
conf_thres=0.25
iou_thres=0.45

lock_mode =False

parser=argparse.ArgumentParser()
opt =parser.parse_args()

model =load_model()
stride =int(model.stride.max())
names = model.module.names if hasattr(model, 'module') else model.names
colors = [[np.random.randint(0, 255) for _ in range(3)] for _ in names]

mouse =pynput.mouse.Controller()

t =Thread(target=recoil_control)
t.start()


with pynput.mouse.Events() as events:
    while True:
        it =next(events)
        while it is not None and not isinstance(it,pynput.mouse.Events.Click):
            it = next(events)
        if it is not None and it.button == it.button.x2 and it.pressed:
            lock_mode = not lock_mode
            print('lock_mode','on' if lock_mode else 'off')

# def on_move(x, y):
#     pass
#
# def on_click(x, y, button, pressed):
#     global lock_mode
#     if pressed and button ==button.x2:
#         lock_mode =not lock_mode
#         print('lock_mode:','on' if lock_mode else 'off')
#
#
# def on_scroll(x, y, dx, dy):
#     pass
#
# # ...or, in a non-blocking fashion:
# listener = pynput.mouse.Listener(
#     on_move=on_move,
#     on_click=on_click,
#     on_scroll=on_scroll)
# listener.start()

        img0 = grab_screen(region=(0, 0, x, y))
        img0 =cv2.resize(img0,(re_x,re_y))
        img0 =cv2.cvtColor(img0,cv2.COLOR_BGR2RGB)

        img =letterbox(img0,img_size,stride)[0]
        img =img.transpose((2,0,1))[::-1]
        img =np.ascontiguousarray(img)

        img =torch.from_numpy(img).to(device)
        img =img.half() if half else img.float()
        img/=255.
        if len(img.shape) ==3:
            img = img[None]

        pred = model(img,augment=False)[0]
        pred = non_max_suppression(pred,conf_thres, iou_thres)

        aims=[]
        for i, det in enumerate(pred):  # detections per image
            s =''
            s+= '%gx%g' % img.shape[2:]
            gn =torch.tensor(img0.shape)[[1,0,1,0]]
            if len(det):
                det[:,:4] =scale_coords(img.shape[2:],det[:,:4],img0.shape).round()

                for c in det[:,-1].unique():
                    n =(det[:,-1]==c).sum()
                    s+=f"{n} {names[int(c)]}{'s' * (n > 1)}, "

                for *xyxy,conf,cls in reversed(det):
                    xywh = (xyxy2xywh(torch.tensor(xyxy).view(1, 4)) / gn).view(-1).tolist()  # normalized xywh
                    line = (cls, *xywh)  # label format
                    aim =('%g ' * len(line)).rstrip() % line + '\n'
                    aim =aim.split(' ')
                    aims.append(aim)

            if len(aims):
                if lock_mode:
                    lock(aims,mouse,x,y)
                for i ,det in enumerate(aims):
                    tag, x_center, y_center, width, heighth =det
                    print(det)
                    x_center ,width =re_x * float(x_center), re_x * float(width)
                    y_center ,heighth =re_y * float(y_center) , re_y * float(heighth)
                    top_left =(int(x_center-width/2.),int(y_center+heighth/2.))
                    bottom_right =(int(x_center+width/2.),int(y_center-heighth/2.))
                    color =(0,255,0)
                    cv2.rectangle(img0,top_left,bottom_right,color,3)


        cv2.namedWindow('csgo_detect', cv2.WINDOW_NORMAL)
        cv2.imshow('csgo_detect', img0)


        hwnd =win32gui.FindWindow(None,'csgo_detect')
        CVRECT =cv2.getWindowImageRect('csgo_detect')
        win32gui.SetWindowPos(hwnd,win32con.HWND_TOPMOST,0,0,0,0,win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break