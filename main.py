
import os
os.environ['QT_QPA_PLATFORM'] = 'xcb'
os.environ['QT_LOGGING_RULES'] = '*=false'


import cv2
import numpy as np

img = None
point_img = None
clicked_points = []

def start(file):
    global img
    img = cv2.imread(file, cv2.IMREAD_COLOR)
    cv2.imshow('rubic', img)
    add_noise_trackbars()
    cv2.setMouseCallback('rubic', handle_mouse_event)
    while True:
        key = cv2.waitKey(0) & 0xFF

        if key == 27 or key == ord('q'):
            cv2.destroyAllWindows()
            break


def update_noises(val):
    global img
    
    gauss_val = cv2.getTrackbarPos('Gauss', 'rubic')
    sp_val = cv2.getTrackbarPos('SaltAndPepper', 'rubic')
    
    noisy_img = np.copy(img)
    
    if gauss_val > 0:
        noise = np.zeros(noisy_img.shape, np.int16)
        cv2.randn(noise, (0, 0, 0), (gauss_val, gauss_val, gauss_val))
        noisy_img = cv2.add(noisy_img, noise, dtype=cv2.CV_8UC3)
        
    if sp_val > 0:
        prob = sp_val / 100.0
        rnd = np.random.rand(noisy_img.shape[0], noisy_img.shape[1])
        noisy_img[rnd < prob / 2] = [0, 0, 0]
        noisy_img[(rnd >= prob / 2) & (rnd < prob)] = [255, 255, 255]
        
    cv2.imshow('rubic', noisy_img)


def handle_mouse_event(event, x, y, flags, param):
    global img, point_img, clicked_points

    if point_img is None:
        point_img = np.copy(img)

    if event == cv2.EVENT_LBUTTONDOWN:
        if len(clicked_points) == 4:
            point_img = np.copy(img)
            clicked_points = []

        clicked_points.append((x, y))
        cv2.circle(point_img, (x, y), 5, (255, 0, 255), -1)
        cv2.imshow('rubic', point_img)

        if len(clicked_points) == 4:
            print(clicked_points)


def add_noise_trackbars():
    cv2.createTrackbar('Gauss', 'rubic', 0, 100, update_noises)
    cv2.createTrackbar('SaltAndPepper', 'rubic', 0, 100, update_noises)


start("imgs/Rubik01.jpg")