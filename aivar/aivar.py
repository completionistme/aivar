import codecs
import fileinput
import glob
import json
import ntpath
import os
import subprocess
from pathlib import Path
from shutil import copyfile

import cv2
import numpy as np
from pytube import YouTube


class Aivar:
    def __init__(self, job):
        self.job = job

    def process(self):
        self.download_video()
        self.extract_frames()
        self.download_subjects()
        self.prepare_subjects()
        self.search()
        self.publish()

    def download_video(self):
        # download vid
        print('--')
        print('download ' + self.job.vid_url)
        print('  to ' + self.job.download_dir)
        # from: https://stackoverflow.com/a/46562895/580651
        YouTube(self.job.vid_url).streams.first().download(output_path=self.job.download_dir, filename=self.job.job_id)
        print('done')

    def extract_frames(self):
        # extract frames
        print('--')
        print('extract frames to ' + self.job.frames_dir)
        vid = glob.glob(self.job.download_dir + "*.mp4")[0]

        # crop area presets
        bottom_right_crop = 'in_w/4:in_h/3:(in_w/4)*3:(in_h/3)*2'
        top_right_crop = 'in_w/4:in_h/3:(in_w/4)*3:0'
        bottom_left_crop = 'in_w/4:in_h/3:0:(in_h/3)*2'
        top_left_crop = 'in_w/4:in_h/3:0:0'

        # todo: make the crop area an option, e.g. 'tr', 'br', 'bl', 'tl'; class constants
        crop = bottom_right_crop
        subprocess.call(['ffmpeg', '-i', vid, '-vf', 'crop=' + crop + ',fps=1/' + str(self.job.frame_interval_seconds),
                         self.job.frames_dir + '%04d.jpg'])
        print('done')

    def download_subjects(self):
        # delegate to handler
        self.job.handler.download_subjects(self.job)

    def prepare_subjects(self):
        icon_on_screen_size = self.job.icon_on_screen_size

        def r(image):
            new_dim = (icon_on_screen_size, icon_on_screen_size)
            return cv2.resize(image, new_dim, interpolation=cv2.INTER_AREA)

        for subject in glob.glob(self.job.subjects_dir + '*.jpg'):
            cv2.imwrite(subject, r(cv2.imread(subject)))

    def search(self):
        # search for subjects in frames
        results = []
        frames = glob.glob(self.job.frames_dir + "*.jpg")
        subjects = glob.glob(self.job.subjects_dir + "*.jpg")
        for frame in frames:
            for subject in subjects:
                result = self.searchFrame(frame, subject)
                if result:
                    results.append(result)
        self.store_results_json(results)

    def searchFrame(self, frame, subject):
        frame_filename = ntpath.basename(frame)
        subject_filename = ntpath.basename(subject)
        print(frame, subject)
        print('-- searching for ' + subject_filename)
        print('  in ' + frame_filename)

        # from: https://stackoverflow.com/a/15147009/580651
        img_rgb = cv2.imread(frame)
        template = cv2.imread(subject)
        w, h = template.shape[:-1]
        res = cv2.matchTemplate(img_rgb, template, cv2.TM_CCOEFF_NORMED)
        threshold = .90
        loc = np.where(res >= threshold)

        matches = []
        if loc[0].size > 0:
            for pt in zip(*loc[::-1]):  # switch columns and rows
                matches.append({
                    "pos": pt,
                    "w": w,
                    "h": h,
                })
                cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)
            match_file_name = self.job.matches_dir + os.path.splitext(frame_filename)[0] + '-' + \
                              os.path.splitext(subject_filename)[0] + os.path.splitext(frame_filename)[1]
            print(match_file_name)
            cv2.imwrite(match_file_name, img_rgb)
            result = {
                "frame": frame_filename,
                "subject": subject_filename,
            }
            return result
        return

    def store_results_json(self, results):
        # store the whole result to json to be worked with somewhere else
        def default(o):
            if isinstance(o, np.int64): return int(o)
            raise TypeError

        json.dump(results, codecs.open(self.job.results_file, 'w', encoding='utf-8'), separators=(',', ':'),
                  sort_keys=True, indent=4, default=default)
        print('results stored to ' + self.job.results_file)
        print('done')

    def publish(self):
        print('--')
        print('publish')
        index_file = self.job.work_folder + 'index.html'
        copyfile('aivar/index.html', index_file)
        video_id = YouTube(self.job.vid_url).video_id
        subjects = Path(self.job.subjects_file).read_text()
        results = Path(self.job.results_file).read_text()
        with fileinput.FileInput(index_file, inplace=True) as file:
            for line in file:
                print(
                    line.replace('%frame_interval_seconds%', str(self.job.frame_interval_seconds))
                        .replace('%video_id%', video_id)
                        .replace('%subjects%', subjects)
                        .replace('%results%', results)
                    , end='')
        print('done')
