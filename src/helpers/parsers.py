
from payload_schema import *

from helpers.standards import getStandardsMapping
from pprint import pprint
import sys
import inspect


def parseDocument(envelope):

    mapping = getStandardsMapping()

    doc = None

    parser = getParser(envelope)

    if parser:
        doc = parser.parse(envelope, mapping)
    else:
        doc = FetchParser().parse(envelope, mapping)

    return doc


def canParse(envelope):
    return getParser(envelope) is not None

def getParser(envelope):

    schemas = {schema.lower() for schema in envelope.get('payload_schema', [])}

    if 'nsdl_dc' in schemas:
        return NsdlDcParser()

    elif 'lrmi' in schemas and not "json-ld" in schemas:
        return LrmiParser()

    elif "bookshare.org json-ld" in schemas:
        return JsonLdParser()

    elif "a11y-jsonld" in schemas or "json-ld" in schemas:
        return JsonLdParser()

    elif "lom" in schemas:
        return LomParser()

    return None


