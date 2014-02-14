from celery.task import task
from celery.log import get_default_logger
from celery import group, chain, chord
from celeryconfig import config

import pyes

import urlparse
import urllib2
import requests
import hashlib

from BeautifulSoup import BeautifulSoup
import nltk

import traceback
import subprocess
import os

import copy

import pprint

log = get_default_logger()


conn = pyes.ES(
    config['elasticsearch']['host']+":"+config['elasticsearch']['port'],
    timeout=config['elasticsearch']['timeout'],
    bulk_size=config['elasticsearch']['bulk_size']
)

INDEX_NAME = config['elasticsearch']['index_name']
DOC_TYPE = config['elasticsearch']['doc_type']

def md5_hash(text):
    return hashlib.md5(text).hexdigest()

def _send_doc(doc, doc_id):
    update_function = """
        if(title != null){ctx._source.title = title;}

        if(description != null){ctx._source.description = description;}

        if(publisher != null){ctx._source.publisher = publisher;}

        for(String key : keys){
          if(!ctx._source.keys.contains(key)){
            ctx._source.keys.add(key);
          }
        }
        for(String key : standards){
          if(!ctx._source.standards.contains(key)){
            ctx._source.standards.add(key);
          }
        }
        for(String key : mediaFeatures){
          if(!ctx._source.mediaFeatures.contains(key)){
            ctx._source.mediaFeatures.add(key);
          }
        }
        for(String key : accessMode){
          if(!ctx._source.accessMode.contains(key)){
            ctx._source.accessMode.add(key);
          }
        }"""

    doc['keys'] = set([x for x in doc.get('keys', []) if x is not None])

    for k, v in [('publisher', None), ('mediaFeatures', []), ('accessMode', []), ("description", None), ('standards', [])]:
        if k not in doc:
            doc[k] = v


    if(doc['url']):
        doc['url_domain'] = urlparse.urlparse(doc['url']).netloc

    updateResponse = conn.partial_update(INDEX_NAME, DOC_TYPE, doc_id, update_function, upsert=doc, params=doc)

    print(updateResponse)



def get_html_display(url, publisher):
    try:
        resp = urllib2.urlopen(url)
        if not resp.headers['content-type'].startswith('text/html'):
            return {
                "title": url,
                "description": url,
                "publisher": publisher,
                "url" :url,
                "hasScreenshot": False
                }
        raw = resp.read()
        raw = raw.decode('utf-8')
        soup = BeautifulSoup(raw)
        title = url
        if soup.html is not None and \
                soup.html.head is not None and \
                soup.html.head.title is not None:
            title = soup.html.head.title.string


        description = None

        # search meta tags for descriptions
        for d in soup.findAll(attrs={"name": "description"}):
            print d
            if d['content'] is not None:
                description = d['content']
                break

        # should we not find a description, make one out of the first 100 non-HTML words on the site
        if description is None:
            raw = nltk.clean_html(raw)
            tokens = nltk.word_tokenize(raw)
            description = " ".join(tokens[:100])

        return {
            "title": title,
            "description": description,
            "url": url,
            "publisher": publisher,
            "hasScreenshot": False
        }

    except Exception as ex:
        return {
            "title": url,
            "description": url,
            "publisher": publisher,
            "url": url,
            "hasScreenshot": False
        }

def process_generic(envelope):
    url = envelope['resource_locator']

    doc_id = md5_hash(url)

    keys = envelope['keys']
    standards = []

    try:
        doc = get_html_display(url, envelope['identity']['submitter'])
        doc['keys'] = keys
        doc['standards'] = standards
        return doc
    except Exception as ex:
        traceback.print_exc()
        return {
            "title": url,
            "description": url,
            'publisher': envelope['identity']['submitter'],
            "url" :url,
            "hasScreenshot": False
            }


def indexDoc(envelope, config, parsedDoc):

    try:
        if parsedDoc:
            doc = copy.deepcopy(parsedDoc)

            doc_id = md5_hash(envelope.get('resource_locator'))

            doc['keys'].append(envelope.get('identity', {}).get("owner"))

            _send_doc(doc, doc_id)
    except Exception as ex:
        traceback.print_exc()


    # !!! save_image is effectively an empty stub, when the time comes we can call it again
    # save_image.delay(envelope.get('resource_locator'))

    #normalize casing on all the schemas in the payload_schema array, if payload_schema isn't present use an empty array


@task(queue="image")
def save_image(url):
    doc_id = md5_hash(url)

    # p = subprocess.Popen(" ".xvfb-run", "--auto-servernum", "--server-num=1", "python", "screenshots.py", url, doc_id]), shell=True, cwd=os.getcwd(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # filename = p.communicate()
    # print(filename)
