from aivar.aivar import Aivar
from aivar.handler import SteamHandler
from aivar.job import Job


def steam(video_url, app_id, profile_id, frame_interval_seconds=5, icon_on_screen_size=0):
    Aivar(Job(video_url, SteamHandler(app_id, profile_id), frame_interval_seconds, icon_on_screen_size)).process()
