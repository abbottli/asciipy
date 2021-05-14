#!/usr/bin/python

import os
import sys
from timeit import default_timer as timer

import cv2
import fpstimer
import vlc
from PIL import Image

import ascii


def clear():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')


# get total file size of given frame list
def get_total_size(frames):
    total_size = sum(sys.getsizeof(pixel) for frame in frames if frame is not None for pixel in frame)
    unit = 'b'

    if total_size >= 1024:
        total_size //= 1024

        unit = 'kb'

        if total_size >= 1024:
            total_size //= 1024
            unit = 'mb'

    return f'{total_size}{unit}'


def print_frames(frames, fps=30, loop=True, reference=False, filename=''):
    """
    output frames strings in given list one after the other. basically like a film projector

    depending on the terminal, you may see images overlap or flickering for random reasons.
    playing around with the fps might help out with that

    the reference flag will start up the video in a separate vlc window.
    the terminal might start before the vlc player is ready to play though
    """
    input('Successfully processed video. Press enter to play ascii video...')

    fps_timer = fpstimer.FPSTimer(fps)

    if reference:
        # creating vlc media player object
        media = vlc.MediaPlayer(filename)

        # start playing video
        media.play()
        # time.sleep(.4)

    clear()
    start = timer()
    while True:
        try:
            for frame in frames:
                # clear()  # makes the screen flicker and is super slow
                print(frame, end='')
                fps_timer.sleep()
                # time.sleep(rate)  # not super accurate but w/e
            if not loop:
                break
        except KeyboardInterrupt:
            break
    end = timer()
    print(f'played video for {end - start : .2f}s')


def main():
    if len(sys.argv) < 2:
        raise RuntimeError('Usage: this_script.py <input file>')
    input_filename = sys.argv[1]

    save_frames = False
    loop = False
    reference = False

    if not os.path.exists('resources'):
        os.makedirs('resources')
    if not os.path.exists('resources/frames'):
        os.makedirs('resources/frames')

    cap = cv2.VideoCapture(input_filename)

    total_frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    duration = total_frame_count / fps

    start = timer()
    count = 1
    frames = []
    success, image = cap.read()
    while success:
        frame_name = f'frame{count}.jpg'
        frames.append(ascii.to_ascii_from_image(Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB)), frame_name))

        if save_frames:
            cv2.imwrite(f'resources/frames/{frame_name}', image)  # save frame as JPEG file
        print(f'Read a new frame: {count} out of {total_frame_count}. {count / total_frame_count * 100 : .3f}% done',
              end='\r', flush=True)
        success, image = cap.read()
        count += 1

    end = timer()
    print(f'\nconverted {len(frames)} frames to ascii in {end - start : .2f}s\ntotal size is {get_total_size(frames)}')

    print_frames(frames, fps=fps, loop=loop, reference=reference, filename=input_filename)
    print(f'other stats: total frames={total_frame_count}, fps={fps}, original_duration={duration : .2f}s')


if __name__ == '__main__':
    main()
    print('Done')
    # input('Press enter to exit')
