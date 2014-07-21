#!/usr/bin/env python
import pyes
from celeryconfig import config

es = pyes.ES(
    config['elasticsearch']['host']+":"+config['elasticsearch']['port'],
    timeout=config['elasticsearch']['timeout'],
    bulk_size=config['elasticsearch']['bulk_size']
)

index_name = config['elasticsearch']['index_name']

index_config = {
    'analysis': {
        'analyzer': {
            'default': {
                'tokenizer': 'standard',
                'filter': ['standard', 'lowercase', 'snowball']
            },
            "full_keyword": {
                'tokenizer': 'keyword',
                'filter': ['standard', 'lowercase']
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

    # keys will use standard analyzer to split into individual words
    # keys_full will be the original multi-word key with a simple (lowercase) filter applied
    "keys": {
        "type": "multi_field",
        "path": "just_name",
        "fields": {
            "keys": {
                "index": "analyzed",
                "store": "no",
                "type": "string",
                "analyzer": "standard"
            },
            "keys_full": {
                "index": "analyzed",
                "store": "no",
                "type": "string",
                "analyzer": "full_keyword"
            }
        }
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

    # Grade levels (K, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)
    "grades": {
        "index": "analyzed",
        "type": "string",
        "analyzer": "full_keyword",
        "store": "no",
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
es.delete_index_if_exists(index_name)

# create a new index
es.create_index_if_missing(index_name, { 'index': index_config })

# add mapping properties for lr_doc type
es.put_mapping(config['elasticsearch']['doc_type'] ,{'properties':mapping}, [index_name])
