#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
from datetime import datetime
from threading import Thread, Lock
from pytz import timezone
import pytz
from base64 import b64encode

from twilio.rest import TwilioRestClient

from .utils import get_pokemon_name
from .customLog import printPokemonAlways

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
rare_ids = {2, 5, 6, 130, 131, 103, 9, 59, 145, 146, 143, 144, 80, 3, 6, 45, 68, 31, 76, 110, 89, 108, 122, 112, 83, 78, 71, 68, 112, 113, 114, 115, 137, 26, 65, 139, 53, 36, 8, 38, 62}
notify_ids = rare_ids
#hunting
#notify_ids = notify_ids.union({1, 4, 7, 25, 58, 102, 126, 138, 77, 66, 37})

#EVEE!!!
#notify_ids = notify_ids.union({133})

def check_for_notify(args, pokemons):
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

def notify_new(args, mapResponse):
    pokemons = {}
    cells = mapResponse['responses']['GET_MAP_OBJECTS']['map_cells']
    for cell in cells:
        for p in cell.get('wild_pokemons', []):
            d_t = datetime.utcfromtimestamp((p['last_modified_timestamp_ms'] + p['time_till_hidden_ms']) / 1000.0)
            pokemons[p['encounter_id']] = {
                'encounter_id': b64encode(str(p['encounter_id'])),
                'spawnpoint_id': p['spawn_point_id'],
                'pokemon_id': p['pokemon_data']['pokemon_id'],
                'latitude': p['latitude'],
                'longitude': p['longitude'],
                'disappear_time': d_t
            }

        for f in cell.get('forts', []):
            if 'lure_info' in f:
                lure_expiration = datetime.utcfromtimestamp(f['lure_info']['lure_expires_timestamp_ms'] / 1000.0)
                active_pokemon_id = f['lure_info']['active_pokemon_id']
                encounter_id = f['lure_info']['encounter_id']
                printPokemonAlways(active_pokemon_id, f['latitude'], f['longitude'], lure_expiration)
                pokemons[encounter_id] = {
                    'encounter_id': b64encode(str(encounter_id)),
                    'spawnpoint_id': 'spawn id',
                    'pokemon_id': active_pokemon_id,
                    'latitude': f['latitude'],
                    'longitude': f['longitude'],
                    'disappear_time': lure_expiration
                }    

    if pokemons: 
        check_for_notify(args, pokemons)
