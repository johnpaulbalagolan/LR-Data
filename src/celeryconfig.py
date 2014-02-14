from datetime import timedelta

config = {
    "lrUrl": "https://node01.public.learningregistry.net/harvest/listrecords",
    "couchdb": {
        "dbUrl": "http://localhost:5984/lr-data",
        "standardsDb": "http://localhost:5984/standards",
    },
    "tasks": {
        "insert": "tasks.elasticsearch.save.insertDoc",
        "validation": "tasks.validate.checkWhiteList",
    },
    "redis": {
        "host": "localhost",
        "port": 6379,
        "db": 0
    },
    "elasticsearch": {
        "protocol": "http",
        "host": "localhost",
        "port": "9200",
        "bulk_size": 400,
        "timeout": 30.0
    }
}
# List of modules to import when celery starts.
CELERY_IMPORTS = ("tasks.harvest", "tasks.save", "tasks.validate", "tasks.elasticsearch.save", )

## Result store settings.
## Broker settings.
BROKER_URL = 'amqp://'
CELERY_LOG_DEBUG = "TRUE"
CELERY_LOG_FILE = "./logs/celeryd-%n.log"
CELERY_PID_FILE = "./run/celeryd-%n.pid"
CELERY_LOG_LEVEL = "DEBUG"
BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 30}
#BROKER_POOL_LIMIT = None
CELERY_RESULT_BACKEND = "amqp://"
CELERY_TASK_RESULT_EXPIRES = 1
## Worker settings
## If you're doing mostly I/O you can have more processes,
## but if mostly spending CPU, try to keep it close to the
## number of CPUs on your machine. If not set, the number of CPUs/cores
## available will be used.

CELERYBEAT_SCHEDULE = {
    "harvestLR": {
        "task": "tasks.harvest.startHarvest",
        "schedule": timedelta(hours=1),
        "args": (config,)
    },
}
