import errno
import hashlib
import os

download_folder_name = 'source'
frames_folder_name = 'frames'
subjects_folder_name = 'subjects'
matches_folder_name = 'matches'


class Job:
    def __init__(self, vid_url, handler, frame_interval_seconds=5, icon_on_screen_size=64):
        self.vid_url = vid_url
        self.handler = handler
        self.frame_interval_seconds = frame_interval_seconds
        self.icon_on_screen_size = icon_on_screen_size
        self.job_id = hashlib.sha1(self.vid_url.encode('utf-8')).hexdigest()
        self.work_folder = os.getcwd() + '/jobs/' + self.job_id + '/'
        self.download_dir = self.work_folder + download_folder_name + '/'
        self.frames_dir = self.work_folder + frames_folder_name + '/'
        self.subjects_dir = self.work_folder + subjects_folder_name + '/'
        self.matches_dir = self.work_folder + matches_folder_name + '/'

        self.subjects_file = self.work_folder + 'subjects.json'
        self.results_file = self.work_folder + 'results.json'
        self.result_html_file = self.work_folder + 'index.html'

        self.setup()

    def setup(self):
        try:
            os.makedirs(self.work_folder)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        try:
            os.makedirs(self.download_dir)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        try:
            os.makedirs(self.frames_dir)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        try:
            os.makedirs(self.subjects_dir)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        try:
            os.makedirs(self.matches_dir)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
