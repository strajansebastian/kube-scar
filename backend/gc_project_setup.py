#!/usr/bin/python3

# you should be logged in you google account

import logging
import json
import yaml
import subprocess
import sys

from datetime import datetime
from pymongo import MongoClient

def setup_projects(conf, scan_id):
    logging.basicConfig(
        format=conf['generic']['logging']['format'],
        datefmt=conf['generic']['logging']['date_format'],
        level=conf['generic']['logging']['level']
    )
    
    project_scan_start_time = datetime.now()
    
    for cloud in conf['clouds']:
        logging.debug("Processing cloud type has started %s" % (cloud['type']))
        if cloud['type'] != 'gc':
            logging.debug("Skip processing cloud type %s" % (cloud['type']))
            continue
    
        final_project_list = []
        
        setup_type = '%s-_-%s-_-%s' % (
                cloud['project_setup']['type']['setup'],
                cloud['project_setup']['type']['mechanism'],
                cloud['project_setup']['type']['output']
        )
        
        if setup_type == "dynamic-_-shell-_-json":
            cmd_project = cloud['project_setup']['commands']['project_list']
            
            process = subprocess.Popen(cmd_project, stdout=subprocess.PIPE, stderr=None, shell=True)
            raw_json_project_list, error = process.communicate()
            
            if error != None:
                logging.error("Error getting project list %s" % (error))
                sys.exit(99)
            
            project_list = json.loads(raw_json_project_list)
            
            for project in project_list:
                p_id = project['projectId']
                p_name = project['name']
            
                logging.info("Processing project id %s" % (p_id))
            
                json_project = {
                    "cloud_id": 'gc',
                    "scan_id": scan_id,
                    "type": cloud['project_setup']['type']['setup'],
                    "time": datetime.now(),
                    "project_id": p_id,
                    "other": { 'name': p_name }
                }
                logging.debug(json_project)
        
                final_project_list.append(json_project)
        
        else:
            json_project = {
                "cloud_id": 'gc',
                "scan_id": scan_id,
                "type": 'static',
                "time": datetime.now(),
                "project_id": 'default-static'
            }
            logging.debug(json_project)
        
            final_project_list.append(json_project)
        
        # insert the project list
        mongo_c = MongoClient(conf['generic']['database']['connection'])
        mongo_db = mongo_c[conf['generic']['database']['dbname']]
        mongo_col_projects = mongo_db["projects"]
        
        m_p_id = mongo_col_projects.insert_many(final_project_list)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("You must specify 2 arguments!")
        print("The 1st represents the location of the YAML configuration file!")
        print("The 2nd represents the id of the current scan!")
        sys.exit(99)

    conf = yaml.safe_load(open(sys.argv[1]))
    scan_id = sys.argv[2]

    setup_projects(conf, scan_id)
