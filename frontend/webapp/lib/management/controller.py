import yaml
import logging

from bson.objectid import ObjectId
from datetime import datetime
from pymongo import MongoClient, DESCENDING 

KUBE_SCAR_WEB_CONF='/app/config.yaml'
conf = yaml.safe_load(open(KUBE_SCAR_WEB_CONF))
 
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=10
)

def commands():
    mongo_c = MongoClient(conf['database']['connection'])
    mongo_db = mongo_c[conf['database']['dbname']]

    final_result = []
    coms = mongo_db['setup_commands'].find()

    for com in coms:
        tmp_c_info = {
            'type': com['type'],
            'name': com['name'],
            'description': com['description']
        }
        final_result.append(tmp_c_info)

    return final_result
