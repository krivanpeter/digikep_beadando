
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

    point_img = get_image_to_work_with()
    clicked_points = []


def handle_mouse_event(event, x, y, flags, param):
    global img, noisy_img, point_img, clicked_points

    if point_img is None:
        point_img = get_image_to_work_with()

    if event == cv2.EVENT_LBUTTONDOWN:
        if len(clicked_points) == 4:
            point_img = get_image_to_work_with()
            clicked_points = []

        clicked_points.append({"x": x, "y": y})
        cv2.circle(point_img, (x, y), 10, (255, 0, 255), -1)

        if len(clicked_points) == 4:
            center_points = get_center_points_of_tiles()
            for point in center_points: 
                cv2.circle(point_img, point, 10, (0, 255, 255), -1)
            print_matrix_of_colors(center_points)
        
        cv2.imshow('rubic', point_img)


def print_matrix_of_colors(center_points):
    recognized_colors = get_colors(center_points)
    print("-" * 10)
    print(f"{recognized_colors[0]} | {recognized_colors[1]} | {recognized_colors[2]}")
    print("-" * 10)
    print(f"{recognized_colors[3]} | {recognized_colors[4]} | {recognized_colors[5]}")
    print("-" * 10)
    print(f"{recognized_colors[6]} | {recognized_colors[7]} | {recognized_colors[8]}")
    print("-" * 10)


def get_colors(center_points):
    recognized_colors = []
    for point in center_points:
        x = point[0]
        y = point[1]

        color_sample = get_image_to_work_with()[y - 5 : y + 5, x - 5 : x + 5]
        cleared_bgr = np.median(color_sample, axis=(0,1)).astype(np.uint8)
        pixel_as_image = np.array([[cleared_bgr]])
        pixel_hsv = cv2.cvtColor(pixel_as_image, cv2.COLOR_BGR2HSV)
        hue = pixel_hsv[0][0][0]
        saturation = pixel_hsv[0][0][1]
        value = pixel_hsv[0][0][2]

        letter = '?'
                
        color_ranges = {
            'P': {"hue_ranges": [[0, 2], [170, 179]], "saturation_range": [50, 255], "value_range": [50, 255]},
            'N': {"hue_ranges": [[3, 21]], "saturation_range": [100, 255], "value_range": [100, 255]},
            'S': {"hue_ranges": [[22, 34]], "saturation_range": [100, 255], "value_range": [100, 255]},
            'Z': {"hue_ranges": [[35, 85]], "saturation_range": [32, 255], "value_range": [50, 255]},
            'K': {"hue_ranges": [[100, 140]], "saturation_range": [50, 255], "value_range": [0, 255]},
            'F': {"hue_ranges": [[0, 179]], "saturation_range": [0, 37], "value_range": [151, 255]}
        }

        for key, range in color_ranges.items():
            s_min, s_max = range["saturation_range"]
            v_min, v_max = range["value_range"]
            
            if not (s_min <= saturation <= s_max and v_min <= value <= v_max):
                continue 
                
            hue_talalat = False
            for h_min, h_max in range["hue_ranges"]:
                if h_min <= hue <= h_max:
                    hue_talalat = True
                    break
                    
            if hue_talalat:
                letter = key
                break

        """
        if letter == '?':
        print(f"Position: {point}, H: {hue}, S: {saturation}, V: {value}")
        """
        
        recognized_colors.append(letter)

    return recognized_colors


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
            
            current_center_point_x = top_edge_x + i * (bottom_edge_x - top_edge_x)
            current_center_point_y = top_edge_y + i * (bottom_edge_y - top_edge_y)
            
            pixel_x = int(current_center_point_x)
            pixel_y = int(current_center_point_y)
            
            tile_center_points.append((pixel_x, pixel_y))
    
    return tile_center_points


def get_image_to_work_with():
    global img, noisy_img

    if noisy_img is None:
        return np.copy(img)
    else:
        return np.copy(noisy_img)


def add_noise_trackbars():
    cv2.createTrackbar('Gauss', 'rubic', 0, 100, update_noises)
    cv2.createTrackbar('SaltAndPepper', 'rubic', 0, 100, update_noises)


start("imgs/Rubik01.jpg")
#start("imgs/Rubik02.jpg")
#start("imgs/Rubik03.jpg")
#start("imgs/Rubik04.png")