#!/usr/bin/env python

import sys
import kodijson
import json
import os
import time
import datetime

from prometheus_client import start_http_server
from prometheus_client import Gauge

KODI_URL = os.environ["KODI_URL"]

port = 9101

if "PROMETHEUS_PORT" in os.environ.keys():
  if type(os.environ["PROMETHEUS_PORT"]) == str:
    port = int(os.environ["PROMETHEUS_PORT"])

start_http_server(port)


k = kodijson.kodijson.Kodi(KODI_URL)

m_playing = Gauge('kodi_playing', 'something is playing')
m_video_count = Gauge('kodi_video_count', 'number of items in the library', ['type'])

def playing():
  players = k.Player.GetActivePlayers()
  result = {
    "playing": False
  }

  if len(players['result']) == 0:
    return result

  player_id = players['result'][0]['playerid']
  speed = k.Player.GetProperties(playerid=player_id, properties=['speed', 'time'])
  loaded = k.Player.GetItem(playerid=player_id)

  if speed['result']['speed'] > 0:
    result['playing'] = True

  if loaded['result']['item']['type'] != 'unknown':
    result['item'] = {
      "type": loaded['result']['item']['type'],
      "id": loaded['result']['item']['id'],
      "label": loaded['result']['item']['label']
    }

  return result


def movie_count():
  movies = k.VideoLibrary.GetMovies()
  return len(movies['result']['movies'])

def tv_count():
  movies = k.VideoLibrary.GetTVShows()
  return len(movies['result']['tvshows'])

def episode_count():
  movies = k.VideoLibrary.GetEpisodes()
  return len(movies['result']['episodes'])

while True:
  playing_result = playing()
  if playing_result['playing']:
    m_playing.set(1)
  else:
    m_playing.set(0)

  minute = datetime.datetime.now().minute
  if minute % 15 == 0:
    m_video_count.labels('movie').set(movie_count())

  if minute % 15 == 5:
    m_video_count.labels('tvshows').set(tv_count())

  if minute % 15 == 10:
    m_video_count.labels('episodes').set(episode_count())

  time.sleep(60)
