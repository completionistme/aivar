import hashlib
import os
from urllib import parse as urlparse

from aivar.helpers import create_dir
from aivar.logger import info, section, section_end

source_folder_name = 'source'
frames_folder_name = 'frames'
subjects_folder_name = 'subjects'
matches_folder_name = 'matches'


class Job:
    def __init__(self, video_url, handler, frame_interval_seconds=5, icon_on_screen_size=64):
        self.video_url = video_url
        self.job_id = hashlib.sha1(self.video_url.encode('utf-8')).hexdigest()
        self.job_dir = os.path.join(os.getcwd(), 'jobs', self.job_id) 

        self.video_type = self.determine_video_type(video_url)
        self.video_source_name = self.job_id
        self.handler = handler
        self.frame_interval_seconds = frame_interval_seconds
        self.icon_on_screen_size = icon_on_screen_size
        self.source_dir = os.path.join(self.job_dir, source_folder_name)
        self.frames_dir = os.path.join(self.job_dir, frames_folder_name)
        self.subjects_dir = os.path.join(self.job_dir, subjects_folder_name)
        self.matches_dir = os.path.join(self.job_dir, matches_folder_name)

        self.source_file = os.path.join(self.job_dir, 'source.json')
        self.subjects_file = os.path.join(self.job_dir, 'subjects.json')
        self.matches_file = os.path.join(self.job_dir, 'matches.json')
        self.results_file = os.path.join(self.job_dir, 'results.json')
        self.result_html_file = os.path.join(self.job_dir, 'index.html')

        self.video_source_path = os.path.join(self.source_dir, self.video_source_name + '.mp4')
        self.video_source_webm_path = os.path.join(self.source_dir, self.video_source_name + '.webm')
        self.video_poster_path = os.path.join(self.source_dir, self.video_source_name + '.jpg')

        create_dir(self.job_dir)
        section('[job]')
        info('id: ' + self.job_id)
        info('handler: ' + self.handler.type)
        info('video: ' + self.video_type)
        section_end()

    def determine_video_type(self, video_url):
        url = urlparse.urlparse(video_url)
        if url.scheme != "http" and url.scheme != 'https':
            return 'local'
        if any(domain in self.video_url for domain in ['youtu']):
            return 'youtube'
