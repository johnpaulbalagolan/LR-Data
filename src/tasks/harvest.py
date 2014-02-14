from celery.task import task
from celery.log import get_default_logger

from helpers.tasks import getTaskFunction

import redis

import requests
import json
import urllib
from urlparse import urlparse, urlunparse
from datetime import datetime
import traceback

log = get_default_logger()


@task(queue="harvest", ignore_result=True)
def startHarvest(config):
    try:
        lrUrl = config['lrUrl']
        r = redis.StrictRedis(host=config['redis']['host'],
                              port=config['redis']['port'],
                              db=config['redis']['db'])
        fromDate = None
        try:
            fromDate = r.get('lastHarvestTime')
        except:
            pass
        until = datetime.utcnow().isoformat() + "Z"
        r.set("lastHarvestTime", until)
        urlParts = urlparse(lrUrl)
        params = {"until": until}
        if fromDate is not None:
            params['from'] = fromDate
        newQuery = urllib.urlencode(params)
        lrUrl = urlunparse((urlParts[0],
                            urlParts[1],
                            urlParts[2],
                            urlParts[3],
                            newQuery,
                            urlParts[5]))
        harvestData.delay(lrUrl, config)
    except Exception as ex:
        traceback.print_exc()
        # retry the last request when things fail
        # (likely caused by JSON parse error due to an LR truncation bug)
        startHarvest.retry(exc=ex, countdown=10, max_retries=5)


@task(queue="harvest", ignore_result=True)
def harvestData(lrUrl, config, enqueueValidate = True):
    try:
        r = redis.StrictRedis(host=config['redis']['host'],
                              port=config['redis']['port'],
                              db=config['redis']['db'])

        print ("Harvesting with url: %s" % lrUrl)

        request = requests.get(lrUrl)

        data = request.json()

        for i in data['listrecords']:
            envelope = i['record']['resource_data']
            r.sadd("harvested_docs", envelope['doc_ID'])

            validateFunc = getTaskFunction(config, 'validate')

            if enqueueValidate:
                validateFunc.delay(envelope, config)
            else:
                validateFunc(envelope, config)


        if "resumption_token" in data and \
            data['resumption_token'] is not None and \
            data['resumption_token'] != "null":
                urlParts = urlparse(lrUrl)
                rawQuery = {"resumption_token": data['resumption_token']}
                newQuery = urllib.urlencode(rawQuery)
                lrUrl = urlunparse((urlParts[0],
                                    urlParts[1],
                                    urlParts[2],
                                    urlParts[3],
                                    newQuery,
                                    urlParts[5]))
                harvestData.delay(lrUrl, config)
    except Exception as exc:
        traceback.print_exc()

        # on request fails, retry the request in 10 seconds.  Most fails are due to a
        # JSON parse error caused by truncated LR requests.

        harvestData.retry(exc=exc, countdown=10, max_retries=5)
