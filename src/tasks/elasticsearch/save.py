from celery.task import task
from celery.log import get_default_logger
from celery import group, chain, chord
from celeryconfig import config

import pyes

import urlparse
import hashlib

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
        }
        for(String grade : grades){
          if(!ctx._source.grades.contains(grade)){
            ctx._source.grades.add(grade);
          }
        }"""

    for k, v in [('publisher', None), ('mediaFeatures', []), ('accessMode', []), ("description", None), ('standards', []), ('grades', [])]:
        if k not in doc:
            doc[k] = v

    doc['keys'] = set([x for x in doc.get('keys', []) if x is not None])
    doc['grades'] = set([x for x in doc.get('grades', []) if x is not None])
    doc['standards'] = set([x for x in doc.get('standards', []) if x is not None])

    if(doc['url']):
        doc['url_domain'] = urlparse.urlparse(doc['url']).netloc

    updateResponse = conn.partial_update(INDEX_NAME, DOC_TYPE, doc_id, update_function, upsert=doc, params=doc)

    print(updateResponse)


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
