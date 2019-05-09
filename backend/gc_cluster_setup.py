#!/usr/bin/python3

# you should be logged in you google account

import logging
import json
import yaml
import subprocess
import sys

from datetime import datetime
from pymongo import MongoClient

def setup_cluster(conf, cloud_id, project_id, scan_id):
    logging.basicConfig(
        format=conf['generic']['logging']['format'],
        datefmt=conf['generic']['logging']['date_format'],
        level=conf['generic']['logging']['level']
    )
    
    mongo_c = MongoClient(conf['generic']['database']['connection'])
    mongo_db = mongo_c[conf['generic']['database']['dbname']]
    
    mongo_col_projects = mongo_db["projects"]
    mongo_col_kube_clusters = mongo_db["kube_clusters"]
    
    for cloud in conf['clouds']:
        logging.debug("Processing cloud type has started %s" % (cloud['type']))
        if cloud['type'] != cloud_id:
            logging.debug("Skip processing cloud type %s" % (cloud['type']))
            continue
    
        aggregation = [
            { '$match': { 'cloud_id': cloud_id } },
            { '$group': { '_id': "$project_id", 'max': { '$max': '$scan_start_time' } } }
        ]
        project_list = mongo_col_projects.aggregate(aggregation)
    
        for proj in project_list:
            proj_id = proj['_id']
            logging.info("Processing project id %s" % (proj_id))
    
            if project_id == 'all':
                # do nothing
                pass
            elif project_id != proj_id:
                continue
        
            cmd_cluster = cloud['cluster_setup']['commands']['cluster_list'] % (proj_id)
            process = subprocess.Popen(cmd_cluster, stdout=subprocess.PIPE, stderr=None, shell=True)
            raw_json_container_cluster_list, error = process.communicate()
        
            if error != None:
                logging.error("Error getting container clusters for project id %s. Error: %s" % (p_id, error))
                sys.exit(99)
        
            container_cluster_list = json.loads(raw_json_container_cluster_list)
            save_ccl = []
        
            for cc in container_cluster_list:
                cc_result = {
                    'project_id': proj_id,
                    'scan_id': scan_id,
                    'time': datetime.now()
                }
                for ck in cloud['cluster_setup']['cluster_key_list']:
                    cc_result[ck] = cc[ck]
                save_ccl.append(cc_result)
        
            if len(save_ccl) > 0:
                logging.debug("For project %s there are %s clusters defined!" % (proj_id, len(save_ccl)))
                mongo_col_kube_clusters.insert_many(save_ccl)
            else:
                logging.debug("No clusters found for project %s" % (proj_id))

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("You must specify 3 arguments!")
        print("1st represents the location of the YAML configuration file!")
        print("2nd represents the cloud_id for which you want to do the scan!")
        print("3rd represents the project_id for which you want to do the scan!")
        sys.exit(99)
    
    conf = yaml.safe_load(open(sys.argv[1]))
    cloud_id = sys.argv[2]
    project_id = sys.argv[3]
    
