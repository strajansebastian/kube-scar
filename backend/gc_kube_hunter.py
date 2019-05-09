#!/usr/bin/python3

import logging
import json 
import yaml
import subprocess
import sys

from datetime import datetime
from pymongo import MongoClient, DESCENDING

def scan_kube_hunter(conf, cloud_id, project_id, scan_id, cluster_scan_id):
    logging.basicConfig(
        format=conf['generic']['logging']['format'],
        datefmt=conf['generic']['logging']['date_format'],
        level=conf['generic']['logging']['level']
    )
    
    mongo_c = MongoClient(conf['generic']['database']['connection'])
    mongo_db = mongo_c[conf['generic']['database']['dbname']]
    
    for cloud in conf['clouds']:
        logging.debug("Processing cloud type %s has started" % (cloud['type']))
        if cloud['type'] != cloud_id:
            logging.debug("Skip processing cloud type %s" % (cloud['type']))
            continue

        logging.debug(scan_id)
        logging.debug(project_id)
        logging.debug(cloud_id)

        endpoint_targets = mongo_db['kube_clusters'].find({'project_id': project_id, 'scan_id': cluster_scan_id})
        logging.debug(endpoint_targets)

        logging.debug('Working on project %s' % (project_id))
        if endpoint_targets.count() < 1:
            logging.debug('Project %s has no endpoints!' % (project_id))
        else: 
            for et in endpoint_targets:
                cmd_khunter = cloud['scans']['kube-hunter']['command'] % (et['endpoint'])
            
                logging.debug('Start scan for cluster %s (%s); command: "%s"' % (et['name'], et['endpoint'], cmd_khunter))
                process = subprocess.Popen(cmd_khunter, stdout=subprocess.PIPE, stderr=None, shell=True)
                raw_json, error = process.communicate()
            
                if error != None:
                    logging.error("Error getting scan result for %s! Error %s" % (project_id, error))
                    sys.exit(99)
            
                json_result = json.loads(raw_json)
                mongo_db['kube_hunter'].insert_one({
                    'project_id': project_id,
                    'scan_id': scan_id,
                    'cluster_id': et['name'],
                    'time': datetime.now(),
                    'result': json_result
                })

if __name__ == '__main__':
    if len(sys.argv) != 5:
        print("You must specify 4 arguments!")
        print("1st represents the location of the YAML configuration file!")
        print("2nd represents the cloud_id for which you want to do the scan!")
        print("3rd represents the project_id for which you want to do the scan!")
        print("4th represents the scan_id for which you want to do the scan!")
        sys.exit(99)
    
    conf = yaml.safe_load(open(sys.argv[1]))
    cloud_id = sys.argv[2]
    project_id = sys.argv[3]
    scan_id = sys.argv[4]
    scan_kube_hunter(conf, cloud_id, project_id, scan_id)

