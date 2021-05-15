#!/usr/bin/python

import argparse
import math
import multiprocessing as mp
import os
from timeit import default_timer as timer

import cv2
from PIL import Image

import ascii
import video
from util.CharType import CharType
from util.ImageType import ImageType


def process_frame_range(input_filename, frames_per_process, process_number, q, save_frames=False,
                        char_type=CharType.BRAILLE, image_type=ImageType.DITHER, invert=True):
    """
    Process the range of images for given video
    """
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
            cv2.imwrite(f'resources/frames/{frame_name}', image)  # save frame
    cap.release()


def frame_joiner(frames, q):
    """
    Read from shared queue and set up the frames list until the kill message is received, then put the frames list
    onto the queue for the parent process to use
    """
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


def main():
    # set up input parameters
    parser = argparse.ArgumentParser(description="Displays video in terminal")
    parser.add_argument('file', help='input file')
    parser.add_argument('-loop', action='store_true', help='loop video')
    parser.add_argument('-ref', action='store_true', help='display reference video.'
                                                          ' need to add delay to sync properly with vlc player')
    parser.add_argument('-invert', action='store_false', help='invert video colors. assuming the text is white')
    parser.add_argument('-char', default='braille',
                        choices=[x.name.lower() for x in CharType],
                        help='character conversion type')
    parser.add_argument('-image', default='dither',
                        choices=[x.name.lower() for x in ImageType],
                        help='image conversion type')
    parser.add_argument('-fps', type=int, help='override display fps')

    args = parser.parse_args()

    # configs
    input_filename = args.file
    char_type = CharType[args.char.upper()]
    image_type = ImageType[args.image.upper()]
    invert = args.invert
    loop = args.loop
    reference = args.ref
    save_frames = False
    fps = args.fps

    # folder setup
    if not os.path.exists('resources'):
        os.makedirs('resources')
    if not os.path.exists('resources/frames'):
        os.makedirs('resources/frames')
    if not os.path.exists('resources/output'):
        os.makedirs('resources/output')

    # temp open video to get some property values
    cap = cv2.VideoCapture(input_filename)

    # get video properties
    total_frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if fps is None:
        fps = cap.get(cv2.CAP_PROP_FPS)
    duration = total_frame_count / fps
    cap.release()

    # init frames storage
    frames = [None] * total_frame_count

    # multiprocessing setup
    process_count = mp.cpu_count()
    manager = mp.Manager()
    q = manager.Queue()
    pool = mp.Pool(process_count)  # payment search endpoint has a rate limit so this can't be too high

    listener = pool.apply_async(frame_joiner, (frames, q))

    # fire off workers
    jobs = []
    start = timer()
    frames_per_process = math.ceil(total_frame_count / process_count)

    for i in range(process_count):
        # each process is given a range of frames to convert
        job = pool.apply_async(process_frame_range, (input_filename, frames_per_process, i, q,
                                                     save_frames, char_type, image_type, invert))
        jobs.append(job)

    # collect results from the workers through the pool result queue
    for job in jobs:
        job.get()

    # now we are done, kill the listener
    q.put('kill')
    print('\nRetrieving frame data')
    frames = q.get()  # get data back from listener
    listener.get()
    pool.close()
    pool.join()

    end = timer()
    print(f'\nconverted {len(frames)} frames to ascii in {end - start : .2f}s')
    # increase fps to > 30 if the video starts flickering or if you can see overlapping images

    video.print_frames(frames, fps=fps, loop=loop, reference=reference, filename=input_filename)
    print(f'other stats: total frames={total_frame_count}, fps={fps}, original_duration={duration : .2f}s')


if __name__ == '__main__':
    main()
    print("Done")
