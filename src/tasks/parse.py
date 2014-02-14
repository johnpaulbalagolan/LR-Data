from celery.task import task
from celery.log import get_default_logger
from celery import group, chain, chord
from celeryconfig import config

import traceback
from helpers.parsers import parseDocument


log = get_default_logger()

def parseEnvelope(envelope, config, parsedDoc):

    try:
        parsedDoc.update(parseDocument(envelope))

    except Exception as ex:
        traceback.print_exc()
