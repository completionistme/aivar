import codecs
import fileinput
import glob
import json
import os
import webbrowser
from pathlib import Path
from shutil import copy, copyfile

import ffmpeg
import numpy as np
from cv2 import cv2
from pytube import YouTube

from aivar.helpers import create_dir
from aivar.json import store_json
from aivar.logger import error, highlight, info, progress, section, section_end, success, warn


class Aivar:
    def __init__(self, job):
        self.job = job
        self.matched_subject_size = 0

    def process(self):
        self.prepare()
        self.search()
        self.publish()

    def prepare(self):
        section('[prepare]')
        self.download_video()
        self.prepare_video()
        self.download_subjects()
        section_end()

    def search(self):
        section('[search]')
        self.search_areas()
        section_end()

    def publish(self):
        section('[publish]')
        self.collect_results()
        self.publish_html()
        section_end()

    # == prepare

    def download_video(self):
        if os.path.isfile(self.job.video_source_path):
            success('source video exists')
            return

        info('downloading "' + self.job.video_url + '"...')
        create_dir(self.job.source_dir)

        if self.job.video_type == 'youtube':
            # from: https://stackoverflow.com/a/46562895/580651
            YouTube(self.job.video_url).streams.first() \
                .download(output_path=self.job.source_dir, filename=self.job.job_id)

        if self.job.video_type == 'local':
            extension = Path(self.job.video_url).suffix
            copy(self.job.video_url, os.path.join(self.job.source_dir, self.job.video_source_name + extension))

        success('stored to ' + self.job.source_dir)

    def prepare_video(self):
        self.transcode_video(self.job.video_url, self.job.video_source_path)
        # self.transcode_video(self.job.video_source_path, self.job.video_source_webm_path)
        video_probe = self.get_video_probe()
        width = int(video_probe['width'])
        height = int(video_probe['height'])
        duration = float(video_probe['duration'])
        info('duration: ' + str(duration), 'dimensions: ' + str(width) + 'x' + str(height))
        poster_time = int(float(video_probe['duration']) / 3)
        self.extract_poster(self.job.video_source_path, self.job.video_poster_path, poster_time)

    def probe_video(self, video_file):
        if os.path.exists(self.job.source_file):
            success('source probe info exists')
            return
        info('probing video...')
        probe = ffmpeg.probe(video_file)
        store_json(probe, self.job.source_file)

    def get_video_probe(self):
        if not os.path.exists(self.job.source_file):
            self.probe_video(self.job.video_source_path)
        probe_file = json.loads(Path(self.job.source_file).read_text())
        return next((stream for stream in probe_file['streams'] if stream['codec_type'] == 'video'), None)

    def transcode_video(self, video_file, output):
        if os.path.exists(output):
            return
        info('transcoding video to ' + output + '...')
        try:
            ffmpeg.input(video_file).output(output).run(quiet=False, capture_stderr=True)
        except ffmpeg.Error as err:
            error(codecs.escape_decode(err.stderr)[0].decode("utf-8"))
        exit()

    def extract_poster(self, video_file, output, time):
        if os.path.exists(self.job.video_poster_path):
            success('poster exists')
            return
        info('extracting poster at ...' + str(int(time)))
        try:
            (
                ffmpeg.input(video_file, ss=time)
                    .output(output, vframes=1)
                    .overwrite_output()
                    .run(quiet=True, capture_stderr=True)
            )
        except ffmpeg.Error as err:
            error(codecs.escape_decode(err.stderr)[0].decode("utf-8"))

    def download_subjects(self):
        if os.path.exists(self.job.subjects_dir):
            success('subjects exists')
            return
        create_dir(self.job.subjects_dir)
        # delegate to handler
        self.job.handler.download_subjects(self.job)

    # == search

    def search_areas(self):
        # search bottom right first
        matches = self.search_area('rb')
        # if nothing was found, search top right
        if len(matches) == 0:
            matches = self.search_area('rt')
        store_json(matches, self.job.matches_file)
        # if len(matches) > 0:
        #   self.ocr(matches)

    def search_area(self, area_key):
        info('searching in ' + area_key + ' area ...')
        area_dir = os.path.join(self.job.frames_dir, area_key)
        if not os.path.exists(area_dir):
            self.extract_frames(area_key, area_dir)

        frames = glob.glob(os.path.join(area_dir, "*.jpg"))

        if len(frames) == 0:
            raise ValueError('No frames available. Video too short?')

        # sort frames in reverse - assuming unlocks usually happen later a video
        def file_basename(s):
            return int(os.path.basename(s)[:-4]) * -1

        frames.sort(key=file_basename)

        subjects = glob.glob(os.path.join(self.job.subjects_dir, "*.jpg"))
        return self.ir(frames, subjects)

    def extract_frames(self, area_key, output_dir):
        # extract frames
        info('extracting frames from ' + area_key + ' area ...')

        # area definitions
        crop_areas = {
            'rt': ('(in_w/4)*3', '0', 'in_w/4', 'in_h/3'),
            'rb': ('(in_w/4)*3', '(in_h/3)*2', 'in_w/4', 'in_h/3'),
            'lt': ('0', '0', 'in_w/4', 'in_h/3'),
            'lb': ('0', '(in_h/3)*2', 'in_w/4', 'in_h/3'),
        }

        crop_area = crop_areas.get(area_key)
        create_dir(output_dir)

        # for area_key, crop_area in crop_areas.items():
        try:
            (
                ffmpeg
                    .input(self.job.video_source_path)
                    .crop(*crop_area)
                    .filter('fps', '1/' + str(self.job.frame_interval_seconds))
                    .output(os.path.join(output_dir, '%05d.jpg'))
                    .run(quiet=True, capture_stderr=True)
            )
        except ffmpeg.Error as err:
            # decode error message and print to stdout
            # from: https://stackoverflow.com/a/37059682/580651
            error(codecs.escape_decode(err.stderr)[0].decode("utf-8"))
        success('stored ' + str(len(glob.glob(os.path.join(output_dir, '*.jpg')))) + ' frames to ' + output_dir)

    def ir(self, frames, subjects):
        # search for subjects in frames
        matches = []
        create_dir(self.job.matches_dir)

        info('searching for ' + str(len(subjects)) + ' subjects in ' + str(len(frames)) + ' frames...')

        i = 0
        total = len(subjects) * len(frames)

        for frame in frames:
            for subject in subjects:
                progress(i, total)
                i = i + 1
                match = self.search_frame_ir(frame, subject)
                if match:
                    matches.append(match)
        progress(i, total)

        for result in matches:
            highlight('found subject ' + result.get('subject') + ' (' + str(
                result.get('subject_size')) + 'px) in frame ' + result.get('frame'))

        if len(matches) == 0:
            warn('found nothing :/')

        return matches

    def search_frame_ir(self, frame, subject):
        frame_filename = os.path.basename(frame)
        subject_filename = os.path.basename(subject)

        # from: https://stackoverflow.com/a/15147009/580651
        frame_rgb = cv2.imread(frame)
        subject_rgb = cv2.imread(subject)

        # TODO: resize subject_rgb to different sizes instead of using one fixed size 32-64 pixels
        # TODO: remember in which crop area and with what size a first match was found - use for rest with threshold
        # subject_size = self.job.icon_on_screen_size

        sizes = range(65, 31, -2)

        if self.matched_subject_size > 0:
            sizes = range(self.matched_subject_size, self.matched_subject_size - 1, -1)

        def prep_subject(image, size):
            # subject_rgb_prep = cv2.cvtColor(subject_rgb_prep, cv2.COLOR_BGR2GRAY)
            # subject_rgb_prep = cv2.Canny(subject_rgb_prep, 50, 200)
            return cv2.resize(image, (size, size), interpolation=cv2.INTER_AREA)

        for subject_size in sizes:
            subject_rgb_prep = prep_subject(subject_rgb, subject_size)
            w, h = subject_rgb_prep.shape[:-1]
            res = cv2.matchTemplate(frame_rgb, subject_rgb_prep, cv2.TM_CCOEFF_NORMED)

            # filter out by threshold
            threshold = .8
            loc = np.where(res >= threshold)

            matches = []
            if loc[0].size > 0:
                for pt in zip(*loc[::-1]):  # switch columns and rows
                    matches.append({
                        "pos": pt,
                        "w": w,
                        "h": h,
                    })
                    cv2.rectangle(frame_rgb, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)
                match_file_name = os.path.splitext(frame_filename)[0] + '-' + os.path.splitext(subject_filename)[0] + \
                                  os.path.splitext(frame_filename)[1]
                match_file = os.path.join(self.job.matches_dir, match_file_name)
                cv2.imwrite(match_file, frame_rgb)
                result = {
                    "frame": frame_filename,
                    "subject": subject_filename,
                    "subject_size": subject_size,
                }
                # remember subject size to speed up the process for subsequent frames
                self.matched_subject_size = subject_size
                return result
        return

    def ocr(self, matches):
        info('running ocr for matches...')
        warn('skipping for now')
        # self.search_frame_ocr(frame)

    def search_frame_ocr(self, frame):
        return

    # == publish

    def collect_results(self):
        info('collecting results...')
        # TODO: merge into results.json: matches.json, subjects.json, ocr.json
        # warn('skipping for now')
        store_json('', self.job.results_file)

    def publish_html(self):
        info('generating html...')
        video_id = self.job.video_source_name
        # video_type = self.job.video_type
        # force it to use the local template, even for youtube videos
        video_type = 'local'
        copyfile('templates/template-' + video_type + '.html', self.job.result_html_file)
        if video_type == 'youtube':
            video_id = YouTube(self.job.video_url).video_id
        subjects = Path(self.job.subjects_file).read_text()
        matches = Path(self.job.matches_file).read_text()
        results = Path(self.job.results_file).read_text()
        with fileinput.FileInput(self.job.result_html_file, inplace=True) as file:
            for line in file:
                print(
                    line.replace('%frame_interval_seconds%', str(self.job.frame_interval_seconds))
                        .replace('%video_id%', video_id)
                        .replace('%video_url_mp4%', self.job.video_source_path)
                        .replace('%video_poster_url%', self.job.video_poster_path)
                        .replace('%subjects%', subjects)
                        .replace('%matches%', matches)
                        .replace('%results%', results)
                    , end='')
        success('stored to ' + self.job.result_html_file)
        webbrowser.open('file:///' + self.job.result_html_file, new=2)
