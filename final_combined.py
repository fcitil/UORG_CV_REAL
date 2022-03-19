from ast import Return
from cgitb import text
from distutils.command.config import config
from pyexpat import model
from tkinter import CENTER, Frame
from tkinter.messagebox import NO
from turtle import circle
import numpy as np
from time import time
from PIL import Image
import pytesseract
import imutils
import time
pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
import cv2
import numpy as np

"""
Thins to do:
1-zero division handle
2-***fixing the letter in the screen
3-***take the position and angle of the target and put it into the control function
4-write the control function
5-create the algorithm with movements and delays
6-***fix the arrow angle
7-do not write the digits two after dot
"""

#frame_width = int(cap.get(3))
#frame_height = int(cap.get(4))
#out = cv2.VideoWriter('all_detections.avi',cv2.VideoWriter_fourcc('M','J','P','G'), 25, (frame_width,frame_height))

#out=np.zeros((512,512,3), np.uint8)

def find_tip(points, convex_hull):
    length = len(points)
    indices = np.setdiff1d(range(length), convex_hull)

    for i in range(2):
        j = indices[i] + 2
        if j > length - 1:
            j = length - j
        if np.all(points[j] == points[indices[i - 1] - 2]):
            return tuple(points[j])

def draw_circle(frame, cnt):
    (x,y),radius = cv2.minEnclosingCircle(cnt)
    x,y = int(x),int(y)
    center=(x,y)
    radius = int(radius)
    cv2.circle(frame,center,radius,(0,0,255),5)
    cv2.line(frame,(w_2,h_2),center,(0,255,0),3)
    return frame, [x,y]

def draw_arrow(frame, cnt, per_frame):
    global arrow_angle, x1, y1, detected_numbers
    cv2.drawContours(frame, [cnt], 0, (0,255,0), -1)
    cv2.putText(frame, "arrow detected", detected_coordinates, cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,0), 3, cv2.LINE_AA)
    (x,y),radius = cv2.minEnclosingCircle(cnt)
    center = (int(x),int(y))
    cv2.circle(frame,center,7,(200,255,255),-1)

    peri = cv2.arcLength(cnt, True)
    #approx = cv2.approxPolyDP(cnt, 0.025 * peri, True)
    hull = cv2.convexHull(approx, returnPoints=False)
    sides = len(hull)
    arrow_tip = find_tip(approx[:,0,:], hull.squeeze())

    if arrow_tip and per_frame==0:
        per_frame=1
        cv2.drawContours(frame, [cnt], -1, (0, 255, 0), 3)
        cv2.circle(frame, arrow_tip, 5, (200, 200, 0), cv2.FILLED)
        cv2.line(frame,center,arrow_tip,(0,0,255),2)
        (x1,y1)=center
        (x2,y2)=arrow_tip
        #arrow_angle = int(180*(np.arctan((x1-x2)/(y1-y2))))  #if y1!=y2
        arrow_angle = (np.arctan( (y2-y1)/(x2 - x1)) )* 180 / np.pi
        arrow_angle=abs(arrow_angle)
        if y2<y1:
            if x2<x1:arrow_angle= arrow_angle-90
            else: arrow_angle= 90-arrow_angle
        else:
            if x2<x1:arrow_angle= -arrow_angle-90
            else: arrow_angle= 90+arrow_angle
        
    if abs(arrow_angle)<=20 and abs(x1-w_2)<=300 : #and abs(y1-h_2)<=100
        x,y,w,h = cv2.boundingRect(cnt)
        #ret, thresh = cv2.threshold(blurred, 127, 255, 0)
        cv2.drawContours(blurred, [cnt], -1, (255,255,255), -1)
        cv2.rectangle(frame,(x-w,y),(x+2*w,y+h),(0,255,0),2)
        toOCR = blurred[y:y+h,x-w:x+2*w]
        #_,toOCR =cv2.threshold(toOCR, 0, 255, cv2.THRESH_BINARY+ cv2.THRESH_OTSU )
        _,toOCR =cv2.threshold(toOCR, 50, 255, cv2.THRESH_BINARY )
        options = "--psm 6 outputbase digits"
        is_OCR=1
        #tick_1 = time.time()
        number = pytesseract.image_to_string(toOCR,lang='eng',  config=options)
        #tick_2 = time.time()
        #print(number)
        
        
        try:
            n=int(number)
            detected_numbers.append(n)
            #print(detected_numbers[-3:])
            if detected_numbers[-6:].count(n)>=6:
                cv2.putText(frame, "distance: "+str(n), detected_coordinates_bottom, cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,0), 3, cv2.LINE_AA)
        except:
            pass
    return frame, [x1,y1], arrow_angle

def calc_acc_angle(approx):
    angles=[]
    #print(approx[1][0][0])
    #approx=approx[0]
    for i in range(-1,11):
        pt1x, pt1y = approx[i][0][0], approx[i][0][1]
        pt2x, pt2y = approx[i+1][0][0], approx[i+1][0][1]
        #print(pt1x, pt1y, pt2x, pt2y)
        try:
            angle = (np.arctan( (int(pt1y)-int(pt2y)) / (int(pt1x)-int(pt2x)) ))* 180 / np.pi
        except:
            angle = 90
        angles.append(angle)
    ll = len(angles)
    acc = 0
    for i in range(ll):
        for j in range(i+1, ll):
            a = abs(angles[i]-angles[j])
            if a > 90:
                a = 90 - a
            acc += a
    return acc

def find_sett(approx):
    #finding and comparing the lengths of the contours
    l_list=[] 
    #pt1x, pt1y = approx[0][0][0], approx[1][0][1]
    #pt2x, pt2y = approx[0][0][0], approx[1][0][1]
    #print(pt1x,pt1y,pt2x,pt2y)
    #length = ((int(pt1x)-int(pt2x))**2 + (int(pt1y)-int(pt2y))**2)**(1/2)
    #l_list.append(length)
    #print(approx)
    """
    for i in range(0,11):
        q=1
        pt1x, pt1y = approx[i][0][0], approx[i][0][1]
        pt2x, pt2y = approx[i+1][0][0], approx[i+1][0][1]
        #print(pt1x,pt1y,pt2x,pt2y)
        a=(int(pt1x)-int(pt2x))**2
        b=(int(pt1y)-int(pt2y))**2
        length = (a+b)**(1/2)
        #print(length)
        for j in l_list:
            if j*1.9>=length>=0.85*j:
                q=0
        if q:
            l_list.append(length)
    """
    pt1x, pt1y = approx[0][0][0], approx[1][0][1]
    pt2x, pt2y = approx[0][0][0], approx[1][0][1]
    length = ((int(pt1x)-int(pt2x))**2 + (int(pt1y)-int(pt2y))**2)**(1/2)
    l_list.append(length)
    for i in range(0,11):
        pt1x, pt1y = approx[i][0][0], approx[i][0][1]
        pt2x, pt2y = approx[i+1][0][0], approx[i+1][0][1]
        length = ((int(pt1x)-int(pt2x))**2 + (int(pt1y)-int(pt2y))**2)**(1/2)
        l_list.append(length)
    max_l=max(l_list)
    new_list=sum(i > 0.8*max_l for i in l_list)

    return new_list

def find_line_angle(p_1, p_2, p_3, p_0):
    len0_1 = (p_0[0] - p_1[0])*2 + (p_0[1] - p_1[1])*2
    len1_2 = (p_1[0] - p_2[0])*2 + (p_1[1] - p_2[1])*2

    if len0_1 <= len1_2:
        p_0, p_1 = p_1, p_2

    cv2.line(frame, p_0, p_1, (255, 255, 0), 5)
    angle_line = np.arctan((p_1[1] - p_0[1]) / (p_1[0] - p_0[0]))
    angle_line=abs(angle_line)
    if p_1[1]>p_0[1] and p_1[0]<p_0[0]:
        angle_line = -angle_line
    elif p_1[1]<=p_0[1] and p_1[0]>p_0[0]:
        angle_line = -angle_line

    angle_line = angle_line * 180 / np.pi

    # finding the angle between the direction and vertical axis in degree
    #right angle is positive left angle is negative 
    #vertical is 0
    if angle_line>0:
        angle_line = angle_line-90
    else:
        angle_line = (90+angle_line)
    return angle_line

def find_line(frame, blurred_complement):
    _, th = cv2.threshold(~blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    contours, hierarchy = cv2.findContours(th, 1, cv2.CHAIN_APPROX_SIMPLE)
    c = max(contours, key=cv2.contourArea)
    #get angle
    blackbox = cv2.minAreaRect(c)
    (x_min, y_min), (w_min, h_min), angle_line = blackbox
    box = cv2.boxPoints(blackbox)
    box = np.int0(box)
    p_1, p_2, p_3, p_0, = box
    angle_line=find_line_angle(p_1, p_2, p_3, p_0)
    #cv2.circle(frame,p_0, 10, (0,255,0), -1)
    #cv2.drawContours(frame, [box], 0, (0, 0, 255), 1)

    #finding the center of the contour with maximum area
    if len(contours)>0:    
        M = cv2.moments(c)
        cx = int(M['m10'] / M['m00'])
        cy = int(M['m01'] / M['m00'])   
        #drawing line to show center of the contour with maximum area
        cv2.line(frame, (cx, 0), (cx, h), (255, 0, 0), 1)
        cv2.line(frame, (0, cy), (w, cy), (255, 0, 0), 1)
        cv2.line(frame, (cx, 0), (cx, h), (255, 0, 0), 1)
        cv2.line(frame, (0, cy), (w, cy), (255, 0, 0), 1)

    cv2.putText(frame,'Angle:'+str(angle_line),(10,60),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,0),2,cv2.LINE_4)
    return frame, [cx,cy], angle_line



def takeoff():
    return None
    
def land():
    return None

def move_cm(target_x, target_y):
    #current_state+x
    #control()
    return None

def move_pix(target_x, target_y=700):
    y_distance=h_2-target_y
    x_distance=target_x-w_2
    
    while abs(x_distance)>=x_thresh or abs(y_distance)>=y_thresh:
        move_cm(x_distance,y_distance)
    
    #move_cm()
    return None

def follow_line(target_x, target_angle):
    rotate(target_angle)
    move_pix(target_x)
    return None
    

def rotate(target_angle):
    #rotate
    return None

def stop():
    #stop movement
    return None


x_thresh=200
y_thresh=200

#h,w= 720,1280
h,w= 352,640
h_2=int(h/2)
w_2=int(w/2)

was_arrow=0
is_OCR=0
area_threshold=10000

detected_coordinates=(10,50)
detected_coordinates_bottom=(10,85)
mode_coordinates=(int(6*w/8),50)
mode="initializing"
hold_this_frame=3
frame_nmb=0
remaining_frame=1
letter=None
arrow_angle=None
target_center=[0,0]
target_angle=360

detected_numbers=[0,0,0,0,0]
h_time=0

cap=cv2.VideoCapture("D:/team/UORG/project.avi.avi")  #   project.avi.avi new_video.mp4
while(True):
    ret,frame=cap.read()
    if remaining_frame>0: remaining_frame-=1
    #print(remaining_frame)
    per_frame=0
    """
    h,w,c=frame.shape
    h_2=int(h/2)
    w_2=int(w/2)
    print(h,w)
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 50, 200, 255)
    ret, thresh = cv2.threshold(edged, 127, 255, 0)
    contours,_=cv2.findContours(thresh, cv2.RETR_TREE,cv2.CHAIN_APPROX_TC89_L1)

    biggest_area=area_threshold
    circle_cnt=None
    cnt2draw_1=None
    cnt2draw_2=None
    cnt2draw_3=None
    detected_shape_nmb=0
    circle_detected=0

    for cnt in contours:
        if detected_shape_nmb==4:
            break
        area=cv2.contourArea(cnt)
        if area < area_threshold:
            continue
        
        approx=cv2.approxPolyDP(cnt, 0.01*cv2.arcLength(cnt,True), True) #0.01 can be changed
        len_approx = len(approx)
        
        #circle detection
        if len_approx>13 and area>=biggest_area:  #to draw all circles change biggest_area with area_threshold and uncomment below line                  
            #frame = draw_circle(frame,cnt)
            biggest_area=area
            cnt2draw_1=cnt
            circle_detected=1  
        #arrow detection
        elif len_approx==7: 
            was_arrow=1
            cnt2draw_2=cnt
            #detected_numbers=[0,0,0,0,0]
            circle_detected=0
            
        #L detection
        if len_approx==6:
            cnt2draw_3=cnt
            mode = "line following"
            letter="L"
        #T detection
        elif len_approx==8:
            #mode="target"
            cnt2draw_3=cnt
            letter="T"
        #H and X detection
        elif len_approx==12:
            cnt2draw_3=cnt
            acc=calc_acc_angle(approx)
            print("acc",acc)
            """
            x, y, w, h = cv2.boundingRect(cnt)
            #cv2.drawContours(blurred, [cnt2draw_3], 0, (0,255,0), -1)
            toOCR = blurred[y-20:y+h+20,x-20:x+w+20]
            #_,toOCR =cv2.threshold(toOCR, 0, 255, cv2.THRESH_BINARY+ cv2.THRESH_OTSU )
            _,toOCR =cv2.threshold(toOCR, 50, 255, cv2.THRESH_BINARY )
            #options = "--psm 6 outputbase digits"
            custom_config = r'-l eng --oem 3 --psm 10 -c tessedit_char_whitelist="HX" '
            is_OCR=1
            #tick_1 = time.time()
            h_or_x = pytesseract.image_to_string(toOCR,lang='eng',  config=custom_config)
            print(h_or_x)
            """
            sett=find_sett(approx)
            #print("sett:",sett)
            #differing H and X
            if acc>1700 and not was_arrow:
                mode="line following"
                letter="H"
                h_time+=1  
            elif acc<1700:
                mode="arrow following"
                letter="X"
            """
            if  (sett == 1 or sett==2) and not was_arrow: #and h_time<20
                mode="line following"
                letter="H"
                h_time+=1                
            elif sett == 4 or was_arrow:
                mode="arrow following"
                letter="X"
                was_arrow=1
            """
        #increasing the number of detected shapes
        if len_approx>13 or len_approx==7: detected_shape_nmb+=1
        if cnt2draw_3 is not None: detected_shape_nmb+=1
                
    #frame = print_mode(frame, mode)
    
    #line detection:
    if mode=="line following" and detected_shape_nmb<3 : #and circle_detected
        frame, target_center, target_angle =find_line(frame, ~blurred)
        if remaining_frame>0: remaining_frame-=1
        #follow_line(target_center[0], target_angle)

    #printing the mode on the left upper side
    cv2.putText(frame, mode, mode_coordinates, cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,0), 3, cv2.LINE_AA)

    #drawing the biggest circle
    if cnt2draw_1 is not None:
        frame, target_center = draw_circle(frame,cnt2draw_1)
        #move(target_center[0],target_center[1])
    #drawing the arrow
    elif cnt2draw_2 is not None: 
        frame, target_center, target_angle=draw_arrow(frame,cnt2draw_2,per_frame)
        if remaining_frame>0: remaining_frame-=1
        #move(target_center[0],target_center[1], target_angle)
    #drawing the letter
    if cnt2draw_3 is not None:
        remaining_frame+=2
        cv2.drawContours(frame, [cnt2draw_3], 0, (0,255,0), 3)
    #showing the letter in the screen
    if letter is not None and remaining_frame>0:
        cv2.putText(frame, letter, detected_coordinates, cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255,255,0), 3, cv2.LINE_AA)
    print(target_center,target_angle)
    #control(target_center,target_angle)
    
    for_us=frame.copy()
    dif=300
    cv2.rectangle(for_us, (w_2-dif,h_2-dif), (w_2+dif,h_2+dif), (255,0,0), 3)
        
    #drawing plus at the center
    cv2.line(frame,(w_2-15,h_2),(w_2+15,h_2),(0,255,0),3)
    cv2.line(frame,(w_2,h_2-15),(w_2,h_2+15),(0,255,0),3)

    #print(detected_numbers)
    cv2.imshow("frame", frame)
    #cv2.imshow("for_us", for_us)
    per_frame=0
    #if is_OCR:
    #    cv2.imshow("toOCR", toOCR)
    #out.write(frame)
     
    if cv2.waitKey(1)==ord('q'):
        break

cap.release()
#out.release()
cv2.destroyAllWindows()