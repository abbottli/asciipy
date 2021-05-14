#!/usr/bin/python

import os
import sys
import time
from timeit import default_timer as timer

import cv2
from PIL import Image

import ascii


def clear():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')


# get total file size of given frame list
def get_total_size(frames):
    total_size = sum(sys.getsizeof(pixel) for frame in frames for pixel in frame)
    unit = 'b'

    if total_size >= 1024:
        total_size //= 1024

        unit = 'kb'

        if total_size >= 1024:
            total_size //= 1024
            unit = 'mb'

    return f'{total_size}{unit}'


def main():
    if len(sys.argv) < 2:
        raise RuntimeError('Usage: this_script.py <input file>')
    input_filename = sys.argv[1]

    save_frames = False

    if not os.path.exists('resources/frames'):
        os.makedirs('resources/frames')

    cap = cv2.VideoCapture(input_filename)

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    duration = frame_count / fps

    start = timer()
    count = 1
    frames = []
    success, image = cap.read()
    while success:
        frame_name = f'frame{count}.jpg'
        frames.append(ascii.to_ascii_from_image(Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB)), frame_name))

        if save_frames:
            cv2.imwrite(f'resources/frames/{frame_name}', image)  # save frame as JPEG file
        print(f'Read a new frame: {count} out of {frame_count}. {count / frame_count * 100 : .3f}% done',
              end='\r', flush=True)
        success, image = cap.read()
        count += 1

    end = timer()
    print(f'\nconverted {len(frames)} frames to ascii in {end - start : .2f}s\ntotal size is {get_total_size(frames)}')

    input('Successfully processed video. Press enter to play ascii video...')
    clear()
    start = timer()
    repeat = True
    while repeat:
        for frame in frames:
            # clear()
            print(frame, end='')
            time.sleep(1/fps)
    end = timer()
    print(f'finished video in {end - start : .2f}s. original runtime was {duration : .2f}s')
    print(f'other stats: frame count={frame_count}, fps={fps}')


if __name__ == '__main__':
    main()
    print('Done')
    # input('Press enter to exit')
