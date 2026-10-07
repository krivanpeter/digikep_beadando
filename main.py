
import os
os.environ['QT_QPA_PLATFORM'] = 'xcb'
os.environ['QT_LOGGING_RULES'] = '*=false'


import cv2
import numpy as np

img = None
point_img = None
noisy_img = None
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
    global img, noisy_img, point_img, clicked_points
   
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

    point_img = get_image_to_show_circles_on()
    clicked_points = []


def handle_mouse_event(event, x, y, flags, param):
    global img, noisy_img, point_img, clicked_points

    if point_img is None:
        point_img = get_image_to_show_circles_on()

    if event == cv2.EVENT_LBUTTONDOWN:
        if len(clicked_points) == 4:
            point_img = get_image_to_show_circles_on()
            clicked_points = []

        clicked_points.append({"x": x, "y": y})
        cv2.circle(point_img, (x, y), 5, (255, 0, 255), -1)

        if len(clicked_points) == 4:
            center_points = get_center_points_of_tiles()
            for point in center_points: 
                cv2.circle(point_img, point, 3, (0, 255, 255), -1)
                
        cv2.imshow('rubic', point_img)


def get_center_points_of_tiles():
    global clicked_points
    left_top = clicked_points[0]
    right_top = clicked_points[1]
    right_bottom = clicked_points[2]
    left_bottom = clicked_points[3]

    proportions = [1/6, 3/6, 5/6]
    tile_center_points = []

    for i in proportions: 
        for j in proportions:
            top_edge_x = left_top["x"] + j * (right_top["x"] - left_top["x"])
            top_edge_y = left_top["y"] + j * (right_top["y"] - left_top["y"])
            
            bottom_edge_x = left_bottom["x"] + j * (right_bottom["x"] - left_bottom["x"])
            bottom_edge_y = left_bottom["y"] + j * (right_bottom["y"] - left_bottom["y"])
            
            height_point_x = top_edge_x + i * (bottom_edge_x - top_edge_x)
            height_point_y = top_edge_y + i * (bottom_edge_y - top_edge_y)
            
            pixel_x = int(height_point_x)
            pixel_y = int(height_point_y)
            
            tile_center_points.append((pixel_x, pixel_y))
    
    return tile_center_points

def get_image_to_show_circles_on():
    global img, noisy_img

    if noisy_img is None:
        return np.copy(img)
    else:
        return np.copy(noisy_img)


def add_noise_trackbars():
    cv2.createTrackbar('Gauss', 'rubic', 0, 100, update_noises)
    cv2.createTrackbar('SaltAndPepper', 'rubic', 0, 100, update_noises)


start("imgs/Rubik01.jpg")