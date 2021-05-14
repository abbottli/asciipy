#!/usr/bin/python

import argparse
import fpstimer
import multiprocessing as mp
import os
import vlc
from timeit import default_timer as timer

import cv2
from PIL import Image

import ascii
import video
from util.CharType import CharType
from util.ImageType import ImageType


def process_frame_range(input_filename, frames_per_process, process_number, q, save_frames=False,
                        char_type=CharType.BRAILLE, image_type=ImageType.DITHER, invert=True):
    offset = process_number * frames_per_process
    cap = cv2.VideoCapture(input_filename)
    cap.set(cv2.CAP_PROP_POS_FRAMES, offset)  # start at offset

    for i in range(frames_per_process):
        success, image = cap.read()
        if not success:
            # print(f'failed to read frame={offset + i}')
            break
        frame_name = f'frame{i}.jpg'

        frame = ascii.to_ascii_from_image(Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB)), name=frame_name,
                                          char_type=char_type, image_type=image_type, invert=invert)

        response = {
            'frame': frame,
            'index': offset + i
        }

        q.put(response)

        if save_frames:
            cv2.imwrite(f'resources/frames/{frame_name}', image)  # save frame as JPEG file
    cap.release()


def frame_joiner(frames, q):
    count = 0
    total_frames = len(frames)
    while True:  # reads from queue until all workers are done
        response = q.get()
        # print('writer found response={}'.format(response))
        if response == 'kill':
            q.put(frames)  # send data back to main
            break
        count += 1
        frames[response['index']] = response['frame']
        print(f'Processing new frame: {count} out of {total_frames}. {count / total_frames * 100 : .2f}% done',
              end='\r', flush=True)

    print(f'\ntotal size is {video.get_total_size(frames)}')


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

    video.clear()
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
    parser = argparse.ArgumentParser(description="Display video in terminal")
    parser.add_argument('file', help='input file')
    parser.add_argument('-loop', action='store_true', help='loop video')
    parser.add_argument('-ref', action='store_true', help='display reference video')
    parser.add_argument('-invert', action='store_false', help='invert video colors. assuming the text is white')
    parser.add_argument('-char', default='braille',
                        choices=['braille', 'matrix', 'ascii'],
                        help='character conversion type')
    parser.add_argument('-image', default='dither',
                        choices=['dither', 'halftone', 'gray', 'black_white', 'silhouette'],
                        help='image conversion type')

    args = parser.parse_args()

    # configs
    input_filename = args.file
    char_type = CharType[args.char.upper()]
    image_type = ImageType[args.image.upper()]
    invert = args.invert
    loop = args.loop
    reference = args.ref
    save_frames = False

    if not os.path.exists('resources'):
        os.makedirs('resources')
    if not os.path.exists('resources/frames'):
        os.makedirs('resources/frames')
    if not os.path.exists('resources/output'):
        os.makedirs('resources/output')

    # open video to get some property values
    cap = cv2.VideoCapture(input_filename)

    # get video properties
    total_frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    duration = total_frame_count / fps
    cap.release()

    # init frames storage
    frames = [None] * total_frame_count

    process_count = mp.cpu_count()
    manager = mp.Manager()
    q = manager.Queue()
    pool = mp.Pool(process_count)  # payment search endpoint has a rate limit so this can't be too high

    watcher = pool.apply_async(frame_joiner, (frames, q))

    # fire off workers
    jobs = []

    start = timer()
    frames_per_process = (total_frame_count // process_count) + 1  #

    for i in range(process_count):
        job = pool.apply_async(process_frame_range, (input_filename, frames_per_process, i, q,
                                                     save_frames, char_type, image_type, invert))
        jobs.append(job)

    # collect results from the workers through the pool result queue
    for job in jobs:
        job.get()

    # now we are done, kill the listener
    q.put('kill')
    print('\nRetrieving frame data')
    frames = q.get()  # get data back from joiner
    pool.close()
    pool.join()

    end = timer()
    print(f'\nconverted {len(frames)} frames to ascii in {end - start : .2f}s')
    # increase fps to > 30 if the video starts flickering/ you can see overlapping images

    print_frames(frames, fps=fps, loop=loop, reference=reference, filename=input_filename)
    print(f'other stats: total frames={total_frame_count}, fps={fps}, original_duration={duration : .2f}s')


if __name__ == '__main__':
    main()
    print("Done")
