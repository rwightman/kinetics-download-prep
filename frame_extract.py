import argparse
import os
import pdb
import numpy as np
import subprocess
import shutil
from joblib import delayed
from joblib import Parallel
count = 0


def extract(videoname, video_dir, output_dir, fps):
    global count
    video_file = os.path.join(video_dir, videoname)
    frames_dir = os.path.join(output_dir, videoname[:-4])

    if not os.path.exists(frames_dir):
        os.makedirs(frames_dir)

    imglist = os.listdir(frames_dir)
    imglist = [img for img in imglist if img.endswith('.jpg')]


    if len(imglist) < 179:  # very few or no frames try extracting againg
        count += 1
        temp_dir = '/tmp/{}'.format(videoname[:-4])
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        if fps > 0:
            command = 'ffmpeg -y -i {} -q:v 1 -threads 1 -filter:v "scale=if(lte(iw\,ih)\,min(256\,iw)\,-2):if(gt(iw\,ih)\,min(256\,ih)\,-2)" -r {} {}/%06d.jpg'.format(video_file, fps, temp_dir)
        else:
            command = 'ffmpeg -y -threads 1 -i {} -q:v 1 {}/%06d.jpg'.format(video_file, frames_dir)

        # os.system(command)
        try:
            output = subprocess.check_output(
                command, shell=True, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as err:
            return err.output

        imglist1 = os.listdir(temp_dir)
        imglist1 = [img for img in imglist1 if img.endswith('.jpg')]
        print(command)
        print(frames_dir, temp_dir, len(imglist1), len(imglist))
        if len(imglist1)+2>len(imglist):
            shutil.rmtree(frames_dir)
            shutil.move(temp_dir, output_dir)
            # pdb.set_trace()
        else:
            # pdb.set_trace()
            shutil.rmtree(temp_dir)
            
        

    imglist = os.listdir(frames_dir)
    imglist = [img for img in imglist if img.endswith('.jpg')]

    return len(imglist)


def main(video_dir, output_dir, num_jobs=16, fps=30):
    print('MAIN')

    videos = os.listdir(video_dir)
    videos = [v for v in videos if v.endswith('.mp4')]

    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)
    videos = sorted(videos)
    print('Frames to be extracted for ',len(videos), ' videos')
    for i, videoname in enumerate(reversed(videos)):
        numf = extract(videoname, video_dir, output_dir, fps)
        extract(videoname, video_dir, output_dir, fps)
    # status_lst = Parallel(n_jobs=num_jobs)(delayed(extract)(videoname, video_dir, output_dir, fps) for i, videoname in enumerate(videos))
    print('to be done', count)

if __name__ == '__main__':
    description = 'Helper script for downloading and trimming kinetics videos.'
    p = argparse.ArgumentParser(description=description)
    p.add_argument('video_dir', type=str,
                   help='Video directory where videos are saved.')
    p.add_argument('output_dir', type=str,
                   help='Output directory where hf5 db for videos will be saved.')
    p.add_argument('-n', '--num-jobs', type=int, default=16)
    p.add_argument('--fps', type=int, default=30,
                   help='Frame rate at which videos to be extracted')

    main(**vars(p.parse_args()))
