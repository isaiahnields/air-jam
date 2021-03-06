from shutil import rmtree
import json
import numpy as np
import traceback
from os import listdir
import pygame

folder = 'guitar-electric'

# initialize the sounds
sounds = []

pygame.mixer.init()

# iterate over each of the sounds
for file in listdir('./../sound/' + folder):

    # create the new sound and save it
    sound = pygame.mixer.Sound('./../sound/' + folder + '/' + file)

    # save the sound
    sounds.append(sound)

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

# try to erase the previous data
try: rmtree('./../data/live')
except Exception as e: pass

# initialize count and debounce
count = 0
debounce = 0

x_coords = []
y_coords = []

# create a list for right wrist points
RWrists = []

# continuously search for new json files
while True:
    try:
        # try to open the next json file as f
        with open('./../data/live/' + str(count).zfill(12) + '_' + 'keypoints.json') as f:

            # read the poeple from the json object
            people = json.load(f)['people']

            # get the pose key points
            data = people[0]['pose_keypoints_2d'] if people else [0 for _ in range(75)]
            data_copy = data.copy()

            # get the indices for left hip and wrist and right wrist
            lh_idx, lw_idx, rw_idx = KEY_POINTS.index('LHip'), KEY_POINTS.index('RWrist'), KEY_POINTS.index('LWrist')

            # get the current left hip and left wrist points
            LHip = np.array(data[lh_idx * 3: lh_idx * 3 + 2])
            LWrist = np.array(data[lw_idx * 3: lw_idx * 3 + 2])

            # get the current right wrist
            RWrists.append(np.array(data[rw_idx * 3: rw_idx * 3 + 2]))

            # if the length of wrists is more than 5
            if len(RWrists) > 200:

                # remove the first element
                RWrists.pop(0)

            # calculate the wrist velocity for the last half second
            RWristVelocity = np.array([0.0, 0.0]) if len(RWrists) < 5 else (RWrists[-1] - RWrists[0]) / 0.4

            # calculate the left wrist difference from the hip
            handDistance = np.linalg.norm(LHip - LWrist)

            # if the right wrist's downward velocity is more than 0.2
            if RWristVelocity[1] > 0.05 and debounce < 0 and handDistance > 0.05:

                i_prev = 0.05

                # iterate over the sounds
                for sound, i, note in zip(sounds, np.linspace(0.2, 0.8, len(sounds)), listdir('./../sound/' + folder)):

                    # if the hand distance is in the right range
                    if i_prev < handDistance < i:

                        # set the sound volume based on strum speed
                        # sound.set_volume(np.linalg.norm(RWristVelocity))

                        # play the sound
                        sound.play()

                        # print the strum
                        print('Strum:', note.split('.')[0], np.linalg.norm(RWristVelocity))

                    i_prev = i

                # reset the debounce
                debounce = 1000

            # increment count and decrement debounce
            debounce -= 1
            count += 1

            x_coords.append(np.array(data_copy[0::3]))
            y_coords.append(np.array(data_copy[1::3]))

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

            x_avg = np.sort(x_diff)[(len(x_diff) + num_out)//2]
            y_avg = np.sort(y_diff)[(len(y_diff) + num_out)//2]

            speed = x_avg**2 + y_avg**2
            if (debounce < 0 and speed > 0.02):
                debounce = 1000
                print("BASS")
                s = pygame.mixer.Sound('./../sound/jump/BD1050.WAV')
                s.play()

    except FileNotFoundError:
        if count > 0:
            count -= 1

    except json.JSONDecodeError as e:
        pass

    except Exception as e:
        traceback.print_exc()
