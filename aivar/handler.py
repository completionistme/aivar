import codecs
import json
import ntpath
import urllib.request
import xml.etree.cElementTree as ET

import numpy as np
from xmljson import parker


class Handler:
    def download_subjects(self, job):
        raise NotImplementedError("Class %s doesn't implement aMethod()" % self.__class__.__name__)


class SteamHandler(Handler):
    def __init__(self, xml_stats_url):
        super().__init__()
        self.xml_stats_url = xml_stats_url

    def download_subjects(self, job):
        # download subjects
        print('--')
        print('download subjects from ' + self.xml_stats_url)
        print('  to ' + job.subjects_dir)

        # download xml
        stats_xml = job.work_folder + 'stats.xml'
        # urllib.request.urlretrieve(self.xml_stats_url, stats_xml)

        # download iconClosed images
        root = ET.parse(stats_xml).getroot()
        subjects = parker.data(root.find("./achievements"), preserve_root=True).get('achievements').get('achievement')
        for subject in subjects:
            subject_url = subject.get('iconClosed')
            urllib.request.urlretrieve(subject_url, job.subjects_dir + ntpath.basename(subject_url))

        def default(o):
            if isinstance(o, np.int64): return int(o)
            raise TypeError

        # store subjects as json
        json.dump(subjects, codecs.open(job.subjects_file, 'w', encoding='utf-8'), separators=(',', ':'),
                  sort_keys=True, indent=4, default=default)
        print('subjects stored to ' + job.subjects_file)
        print('done')
