import pynput

def lock(aims,mouse,x,y):
    mouse_pos_x,mouse_pos_y =mouse.position
    dist_list =[]
    for det in aims:
        _,x_c,y_c,_,_ =det
        dist =(mouse_pos_x-x*float(x_c))**2+(mouse_pos_y-y*float(y_c))**2
        dist_list.append(dist)

    det = aims[dist_list.index(min(dist_list))]

    tag,x_center,y_center,width,heighth =det
    tag =int(tag)
    x_center,width =x*float(x_center) ,x *float(width)
    y_center ,heighth =y*float(y_center),y*float(heighth)

    if tag ==0 or tag ==2:
        mouse.position =(x_center,y_center)
    elif tag ==1 or tag ==3:
        mouse.position =(x_center,y_center-heighth/6.)

import csv
from threading import Thread
import time

def recoil_control():
    f =csv.reader(open('./gun_path/ak47.csv',encoding='utf-8'))
    ak_path=[]
    for i in  f:
        ak_path.append(i)
    ak_path[0][0]='0'
    ak_path = [[float(i) for i in x] for x in ak_path]
    print(ak_path)
    mouse =pynput.mouse.Controller()
    flag =1
    gun_path_mode =False
    k =-1
    with pynput.mouse.Events() as events:
        for event in events:
            if isinstance(event,pynput.mouse.Events.Click):
                if event.button == event.button.left:
                    if event.pressed:
                        flag =1
                    else:
                        flag =0
                if event.button ==event.button.x1 and event.pressed:
                    gun_path_mode = not gun_path_mode
                    print('gun_path_mode:',gun_path_mode)

            if flag and gun_path_mode ==True:
                i =0
                a =next(events)
                while True:
                    mouse.move(ak_path[i][0]*k,-ak_path[i][1]*k)
                    i+=1
                    if i ==30:
                        break
                    if a is not None and isinstance(a,pynput.mouse.Events.Click) and a == pynput.mouse.Button.left and not a.pressed:
                        break
                    while a is not None and not isinstance(a,pynput.mouse.Events.Click):
                        a =next(events)
                    time.sleep(ak_path[i][2]/1000)
                flag =0





