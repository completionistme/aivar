import glob
import ntpath
import os
import urllib.request
import xml.etree.cElementTree as ET

from xmljson import parker

from aivar.json import store_json
from aivar.logger import info, success, progress


class Handler:

    def __init__(self):
        self.type = 'generic'

    def download_subjects(self, job):
        raise NotImplementedError("Class %s doesn't implement aMethod()" % self.__class__.__name__)


class SteamHandler(Handler):
    def __init__(self, app_id, profile_id):
        super().__init__()
        self.type = 'steam'
        self.xml_stats_url = 'https://steamcommunity.com/profiles/' + profile_id + '/stats/appid/' + app_id + '/?tab=achievements&xml=1'

    def download_subjects(self, job):
        # download subjects
        info('downloading subjects definition from "' + self.xml_stats_url + '"...')

        # download xml
        stats_xml = os.path.join(job.job_dir, 'subjects.xml')
        urllib.request.urlretrieve(self.xml_stats_url, stats_xml)

        # parse xml to json
        root = ET.parse(stats_xml).getroot()
        subjects = parker.data(root.find("./achievements"), preserve_root=True).get('achievements').get('achievement')
        store_json(subjects, job.subjects_file)

        # download icons
        info('downloading subjects...')
        i = 0
        total = len(subjects)
        progress(i, total)
        for subject in subjects:
            subject_url = subject.get('iconClosed')
            urllib.request.urlretrieve(subject_url, os.path.join(job.subjects_dir, ntpath.basename(subject_url)))
            i = i + 1
            progress(i, total)
        success('stored ' + str(len(glob.glob(os.path.join(job.subjects_dir, "*.jpg")))) + ' subjects to ' + job.subjects_dir)
