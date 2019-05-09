#!/usr/bin/python3

# you should be logged in you google account

import logging
import json
import yaml
import sys

from datetime import datetime
from pymongo import MongoClient

from gc_project_setup import setup_projects

if len(sys.argv) != 2:
    print("You must specify 1 argument, which represents the location of the YAML configuration file!")
    sys.exit(99)

conf = yaml.safe_load(open(sys.argv[1]))

logging.basicConfig(
    format=conf['generic']['logging']['format'],
    datefmt=conf['generic']['logging']['date_format'],
    level=conf['generic']['logging']['level']
)

mongo_c = MongoClient(conf['generic']['database']['connection'])
mongo_db = mongo_c[conf['generic']['database']['dbname']]

scan_data = {
    'scan_type': 'project',
    'time': datetime.now(),
    'action': 'start'
}

m_s_id = mongo_db['scans'].insert_one(scan_data)

setup_projects(conf, m_s_id.inserted_id)

del scan_data['_id']
scan_data['action'] = 'end'
scan_data['time'] = datetime.now()
scan_data['start_scan_id'] = m_s_id.inserted_id

m_s_id = mongo_db['scans'].insert_one(scan_data)
