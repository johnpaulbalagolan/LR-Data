from celery.task import task
from celery.log import get_default_logger
log = get_default_logger()
from urlparse import urlparse, urlunparse
from urllib import urlencode
import requests
import re
import os.path
from helpers.tasks import getTaskFunction
from helpers.bloom import getBloomFilter
import helpers.parsers

black_list = set(["bit.ly", "goo.gl", "tinyurl.com", "fb.me", "j.mp", "su.pr", 'www.freesound.org'])
good_codes = [requests.codes.ok, requests.codes.moved, requests.codes.moved_permanently]

# @task(queue="validate")
# def emptyValidate(envelope, config):
#     send_task(config['insertTask'], [envelope, config])

WHITELIST_DOMAINS = "whitelist.txt"
WHITELIST_FILTER_FILE = "whitelist_filter.bloom"

BLACKLIST_DOMAINS = "blacklist.txt"
BLACKLIST_FILTER_FILE = "blacklist_filter.bloom"

# Only index items that we have a valid parser for
def checkParsable(envelope, config, validationResult):
    validationResult['valid'] = helpers.parsers.canParse(envelope)

def translate_url(url_parts):
    r = re.compile("\w+:\d+")
    path = url_parts.path
    content_object_id = r.findall(path)[0]
    new_url_parts = ("https", url_parts.netloc, "Public/Model.aspx", url_parts.params, urlencode({"ContentObjectID": content_object_id}), None)
    return urlunparse(new_url_parts)


# Set whitelisted and blacklisted values on indexable items
def checkWhiteList(envelope, config, validationResult):

    whitelistFilter = getBloomFilter(WHITELIST_DOMAINS, WHITELIST_FILTER_FILE)
    blacklistFilter = getBloomFilter(BLACKLIST_DOMAINS, BLACKLIST_FILTER_FILE)

    parts = urlparse(envelope['resource_locator'])
    if "lr-test-data-slice-jbrecht" in envelope['keys']:
        return
    if parts.netloc == "3dr.adlnet.gov":
        envelope['resource_locator'] = translate_url(parts)


    validationResult['data'].update({
        'whitelisted': parts.netloc in whitelistFilter,
        'blacklisted': parts.netloc in blacklistFilter,
    })

    # For the sake of speed, I'm stopping the request of every site to determine if
    # we should index it. Let's use flagging to determine if a resource is
    # active or not, not this slow (and potentially inaccurate) validation step
    # Not to mention, there are a lot of large files we don't need to download...

    # try:
    #     resp = requests.get(envelope['resource_locator'])
    #     print envelope['resource_locator'], resp.status_code

    #     if resp.status_code not in good_codes:
    #         return
    #         except Exception as ex:
    #     print(ex)
    #     return
