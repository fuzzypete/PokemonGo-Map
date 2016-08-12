#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
from datetime import datetime
from threading import Thread, Lock
from pytz import timezone
import pytz
from twilio.rest import TwilioRestClient

from .utils import get_pokemon_name

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(module)11s] [%(levelname)7s] %(message)s')

log = logging.getLogger(__name__)

ACCOUNT_SID = 'AC373a662f2c1413a184a8d498a72b1443'
AUTH_TOKEN = '084ec512a404bf8c7c8f23356c0722aa'

client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)

pacific = timezone('US/Pacific')
fmt = '%I:%M:%S%p'

notifiedLock = Lock()
notifiedMap = {}

# notify for magikarp, lapros, gyros-whatever
#notify_ids = {129, 130, 131}
#drop everything 
rare_ids = {2, 5, 6, 130, 131, 103, 9, 59, 145, 146, 143, 144, 80, 3, 6, 45, 68, 31, 76, 110, 89, 108, 125, 122, 112, 83, 78, 71, 68, 112, 113, 114, 115, 137, 26, 65, 139, 53, 36, 8, 38, 62}
notify_ids = rare_ids
#hunting
#notify_ids = notify_ids.union({1, 4, 7, 25, 58, 102, 126, 138, 77, 66, 37})

#EVEE!!!
#notify_ids = notify_ids.union({133})

def check_for_notify(pokemons):
    for id, poke in pokemons.iteritems():
        encounterId = poke['encounter_id']
        pokeid = poke['pokemon_id']
        pokename = get_pokemon_name(pokeid)
        notify = False 
        if pokeid in notify_ids:
            notify = True
        if pokeid > 148:
            notify = True
        if notify: 
            with notifiedLock:
                if not encounterId in notifiedMap:
                	maplink = "http://maps.google.com/?q={},{}".format(poke['latitude'], poke['longitude'])
                	disappearTimeUTC = pytz.utc.localize(poke['disappear_time'])
                	disappearTime = disappearTimeUTC.astimezone(pacific).strftime(fmt)
                	message = "Found {} at {}. Disappears at {}".format(pokename, maplink, disappearTime)
             		log.info(message)
             		try:
             			client.messages.create(to = '2069303302', from_ = '2064287851', body = message)
             			client.messages.create(to = '2063725192', from_ = '2064287851', body = message)
             			# client.messages.create(to = '2063725220', from_ = '2064287851', body = message)
             			notifiedMap[encounterId] = True
             		except TwilioRestException as e:
            			log.error(e)

# def notify_new():
#     for pokemon in Pokemon.get_active(None, None, None, None):
#         lastNotify = pokemon['']
#         pokemon_point = LatLng.from_degrees(pokemon['latitude'], pokemon['longitude'])
#         diff = pokemon_point - origin_point
#         diff_lat = diff.lat().degrees
#         diff_lng = diff.lng().degrees
#         direction = (('N' if diff_lat >= 0 else 'S') if abs(diff_lat) > 1e-4 else '') + (
#             ('E' if diff_lng >= 0 else 'W') if abs(diff_lng) > 1e-4 else '')
#         entry = {
#             'id': pokemon['pokemon_id'],
#             'name': pokemon['pokemon_name'],
#             'card_dir': direction,
#             'distance': int(origin_point.get_distance(pokemon_point).radians * 6366468.241830914),
#             'time_to_disappear': '%d min %d sec' % (divmod((pokemon['disappear_time']-datetime.utcnow()).seconds, 60)),
#             'disappear_time': pokemon['disappear_time'],
#             'latitude': pokemon['latitude'],
#             'longitude': pokemon['longitude']
#         }
#         pokemon_list.append((entry, entry['distance']))

# def notify_loop(args):
#     try:
#         while True: 
#             notify_new()
#             time.sleep(1)
#     # This seems appropriate
#     except Exception as e:
#         log.info('{0.__class__.__name__}: {0} - waiting 1 sec(s) before restarting'.format(e))
#         time.sleep(1)
#         notify_loop()
