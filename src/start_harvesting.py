#!/usr/bin/env python

from tasks.harvest import *
from celeryconfig import config

# start the harvest process
startHarvest(config)
