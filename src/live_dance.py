from shutil import rmtree
import json
import numpy as np
import traceback
from os import listdir
import pygame
import sys

folder = 'guitar'

# create the key points
KEY_POINTS = [
            "Nose",
            "Neck",
            "RShoulder",
            "RElbow",
            "RWrist",
            "LShoulder",
            "LElbow",
            "LWrist",
            "MidHip",
            "RHip",
            "RKnee",
            "RAnkle",
            "LHip",
            "LKnee",
            "LAnkle",
            "REye",
            "LEye",
            "REar",
            "LEar",
            "LBigToe",
            "LSmallToe",
            "LHeel",
            "RBigToe",
            "RSmallToe",
            "RHeel",
            "Background"
        ]

group2parts = {"face": ["Nose"],
                "hips": ["RHip", "LHip", "MidHip"],
                "knees": ["LKnee", "RKnee"],
                "elbows": ["LElbow", "RElbow"],
                "hands": ["LWrist", "RWrist"],
                "shoulders": ["LShoulder", "RShoulder"]}

group2threshold = {"face": 0.005,
                    "hips": 0.002,
                    "knees": 0.007,
                    "elbows": 0.01,
                    "hands": 0.02,
                    "shoulders": 0.005}

debounce = {"face": 500,
            "hips": 500,
            "knees": 500,
            "elbows": 500,
            "hands": 500,
            "shoulders": 500}

'''
# try to erase the previous data
try: rmtree('./../data/live')
except Exception as e: print(e)
'''


# initialize count and debounce
count = 0

# create a list for right wrist points
x_coords = []
y_coords = []

# continuously search for new json files
while True:
    try:
        # try to open the next json file as f
        with open('./../data/live/' + str(count).zfill(12) + '_' + 'keypoints.json') as f:
            # read the poeple from the json object
            people = json.load(f)['people']

            # get the pose key points
            data = people[0]['pose_keypoints_2d'] if people else [0 for _ in range(75)]

            x_coords.append(np.array(data[0::3]))
            y_coords.append(np.array(data[1::3]))

            # increment count and decrement debounce
            print(count)
            if (count > 94):
                sys.exit()
            for k in debounce.keys():
                debounce[k] -= 1
            count += 1

            num_out = 0
            for i in range(len(x_coords[-1])):
                if x_coords[-1] == [0,0,0]:
                    num_out += 1

            # if the length of wrists is more than 5
            if len(x_coords) <= 5 or len(y_coords) <= 5:
                continue

            x_coords.pop(0)
            y_coords.pop(0)

            x_diff = np.subtract(x_coords[0], x_coords[-1])
            y_diff = np.subtract(y_coords[0], y_coords[-1])

            for i in range(len(x_diff)):
                x_diff[i] = abs(x_diff[i])
                y_diff[i] = abs(y_diff[i])

            for group in group2parts.keys():
                print(group)
                diff, xdiff, ydiff = 0, 0, 0
                for part in group2parts[group]:
                    index = KEY_POINTS.index(part)
                    xdiff += x_diff[index]
                    ydiff += y_diff[index]
                diff = xdiff**2 + ydiff**2
                print(diff)
                if debounce[group] < 500 and diff > debounce:
                    debounce = 500
                    print(group)

    except FileNotFoundError:
        if count > 0:
            count -= 1

    except json.JSONDecodeError as e:
        pass

    except Exception as e:
        traceback.print_exc()