#!/usr/bin/env python
import pyes
from celeryconfig import config

es = pyes.ES(
    config['elasticsearch']['host']+":"+config['elasticsearch']['port'],
    timeout=config['elasticsearch']['timeout'],
    bulk_size=config['elasticsearch']['bulk_size']
)

index_config = {
    'analysis': {
        'analyzer': {
            'default': {
                'tokenizer': 'standard',
                'filter': ['standard', 'lowercase', 'snowball']
            }
        },
        'filter': {
            'snowball': {
                'type': 'snowball',
                'language': 'English'
            }
        },
    }
}

mapping = {
    # Analyze title field per usual and create an unanalyzed one for sorting purposes
    "title": {
        "type": "multi_field",
        "fields": {
            "title": {
                "index": "analyzed",
                "store": "true",
                "type": "string",
            },
            "title_full": {
                "type": "string",
                "index": "not_analyzed",
            }
        }
    },
    "description": {
        "index": "analyzed",
        "store": "true",
        "type": "string",
    },
    # Analyze publisher field per usual, and create an unanlyzed one for faceting/filtering
    "publisher": {
        "type": "multi_field",
        "fields": {
            "publisher": {
                "index": "analyzed",
                "store": "true",
                "type": "string",
            },
            "publisher_full": {
                "type": "string",
                "index": "not_analyzed",
                "store": "true"
            }
        }
    },
    # Keys will use standard analyzer to split into individual words
    "keys": {
        "index": "analyzed",
        "store": "no",
        "type": "string",
        "analyzer": "standard"
    },
    # Standards will be in the form S0000000, no need to analyze
    "standards": {
        "index": "not_analyzed",
        "store": "no",
        "type": "string",
    },
    # Access modes should be a fixed vocab with multiple words, using the
    # simple analyzer (lowercase) for consistency
    "accessMode": {
        "index": "analyzed",
        "store": "true",
        "type": "string",
        "analyzer": "simple",
        "include_in_all": "false",
    },
    # Media features should be a fixed vocab with multiple words, using using the
    # simple analyzer (lowercase) for consistency
    "mediaFeatures": {
        "index": "analyzed",
        "store": "true",
        "type": "string",
        "analyzer": "simple",
        "include_in_all": "false",
    },

    # url should be unanalyzed for lookup
    "url": {
        "index": "not_analyzed",
        "store": "true",
        "type": "string",
    },

    # url domain for faceting and better search purposes
    "url_domain": {
        "index": "not_analyzed",
        "store": "true",
        "type": "string",
    },

    # Boolean-only values for filtering purposes
    "whitelisted": {
        "index": "not_analyzed",
        "store": "true",
        "type": "boolean",
        "include_in_all": "false",
    },
    "blacklisted": {
        "index": "not_analyzed",
        "store": "true",
        "type": "boolean",
        "include_in_all": "false",
    },
    "hasScreenshot": {
        "index": "not_analyzed",
        "store": "true",
        "type": "boolean",
        "include_in_all": "false",
    },
}

# remove our existing LR index
es.delete_index_if_exists('lr')

# create a new index
es.create_index_if_missing('lr', { 'index': index_config })

# add mapping properties for lr_doc type
es.put_mapping("lr_doc" ,{'properties':mapping}, ["lr"])
