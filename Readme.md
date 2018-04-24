# LR-Data
This is a small utility to help pull the data from the Learning Registry into a datastore of your choice.

# Dependencies
LR-Data requires:
* [RabbitMQ](http://www.rabbitmq.com/)
* [Redis](http://redis.io/)
* [Python](http://www.python.org/)
* [Celery](http://www.celeryproject.org/)

### Platform-Specific Requirements:
On OS X, you will also need `libevent`, which can be installed with homebrew: `brew install libevent`

# Install dependencies - Ubuntu shown as example
	sudo apt-get update
	sudo apt-get install -y virtualenv python-dev libevent-dev libxml2-dev libxmlsec1-dev

# Setup
	# Create virtual environment
	virtualenv env
	. env/bin/activate
	# Install python library requirements
	pip install -U -r requirements.txt

# Configuration
All configuration is done in the src/celeryconfig.py file.  For information of configuring Celery please see their [document](http://celery.readthedocs.org/en/latest/index.html).  For lr-data configuration modify

    config = {

		"lrUrl": "http://lrdev02.learningregistry.org/harvest/listrecords",

		"couchdb":{

			"dbUrl":"http://localhost:5984/lr-data"

		},
		"tasks": {
			"insert": "tasks.save.insertDocumentMongo",

			"validate": "tasks.validate.emptyValidate",
		}

		"redis":{

			"host":"localhost",

			"port":6379,

			"db":0
		}

		"mongodb":{

			"database":"lr",

			"collection":"envelope",

			"host": "localhost",

			"port": 27017,

		},
    }

Customizable tasks are defined in the `tasks` hash.  `validate` is the task name for validating incoming docs.  `insert` is the task you wish to use to save the data

# Startup
There are scripts inside of src to get you started.

*  start\_celery\_workers.sh - will start your default worker threads responsible for harvesting, validating, and saving LR data
*  stop\_celery\_workers.sh - stops workers
*  start\_harvesting.py - sends harvest request into queue for workers to start working

To start harvesting, activate your virtualenv, start the celery workers, then start harvesting request

	cd src
	. ../env/bin/activate
    ./start_celery_workers.sh
    ./start_harvesting.py

Should you want to stop (or pause) the processing you can stop the celery workers:

	./stop_celery_workers.sh

When you want to resume processing, you need only start the celery workers again:

	./start_celery_workers.sh

