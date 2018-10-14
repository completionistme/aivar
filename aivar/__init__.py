from aivar.aivar import Aivar
from aivar.handler import SteamHandler
from aivar.job import Job


def steam(vid_url, profile_id, app_id, frame_interval_seconds, icon_on_screen_size):
    xml_stats_url = 'https://steamcommunity.com/profiles/' + profile_id + '/stats/appid/' + app_id + '/?tab=achievements&xml=1'
    Aivar(Job(vid_url, SteamHandler(xml_stats_url), frame_interval_seconds, icon_on_screen_size)).process()
