import ntpath
import urllib.request
import xml.etree.cElementTree as ET


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
        urllib.request.urlretrieve(self.xml_stats_url, stats_xml)

        # download iconClosed images to subjectsDir
        root = ET.parse(stats_xml).getroot()
        for form in root.findall("./achievements/achievement/iconClosed"):
            subject_file_name = ntpath.basename(form.text)
            urllib.request.urlretrieve(form.text, job.subjects_dir + subject_file_name)
        print('done')
