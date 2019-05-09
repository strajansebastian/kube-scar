#!/usr/bin/python3

# you should be logged in you google account

import logging
import json
import yaml
import subprocess
import sys

from datetime import datetime
from pymongo import MongoClient, DESCENDING

from gc_kube_hunter import scan_kube_hunter

if len(sys.argv) != 4:
    print("You must specify 3 arguments!")
    print("1st represents the location of the YAML configuration file!")
    print("2nd represents the cloud_id for which you want to do the scan!")
    print("3rd represents the project_id for which you want to do the scan!")
    sys.exit(99)

conf = yaml.safe_load(open(sys.argv[1]))
cloud_id = sys.argv[2]
project_id = sys.argv[3]

logging.basicConfig(
    format=conf['generic']['logging']['format'],
    datefmt=conf['generic']['logging']['date_format'],
    level=conf['generic']['logging']['level']
)

mongo_c = MongoClient(conf['generic']['database']['connection'])
mongo_db = mongo_c[conf['generic']['database']['dbname']]

cluster_scan_id = mongo_db['scans'].find_one({ 'scan_type': 'kube_cluster', 'action': 'start'}, sort=[('time', DESCENDING)])

scan_data = {
    'scan_type': 'kube_hunter',
    'time': datetime.now(),
    'action': 'start'
}

m_s_id = mongo_db['scans'].insert_one(scan_data)

scan_kube_hunter(conf, cloud_id, project_id, m_s_id.inserted_id, cluster_scan_id['_id'])

del scan_data['_id']
scan_data['action'] = 'end'
scan_data['time'] = datetime.now()
scan_data['start_scan_id'] = m_s_id.inserted_id

m_s_id = mongo_db['scans'].insert_one(scan_data)

