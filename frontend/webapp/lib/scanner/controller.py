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

def kh_scans():
    mongo_c = MongoClient(conf['database']['connection'])
    mongo_db = mongo_c[conf['database']['dbname']]

    final_result = []
    kh_scans = mongo_db['scans'].find(
        {'scan_type': 'kube_hunter', 'action': 'start'},
        sort=[('time', DESCENDING)]
    )

    for khs in kh_scans:
        tmp_scan_info = kh_scan_info(khs['_id'])
        final_result.append(tmp_scan_info)

    return final_result

def kh_scan_info(scan_id):
    if type(scan_id).__name__ != 'ObjectId':
        scan_id = ObjectId(scan_id)

    mongo_c = MongoClient(conf['database']['connection'])
    mongo_db = mongo_c[conf['database']['dbname']]

    khs_start = mongo_db['scans'].find({'scan_type': 'kube_hunter', 'action': 'start', '_id': scan_id})
    khs_stop = mongo_db['scans'].find({'scan_type': 'kube_hunter', 'action': 'end', 'start_scan_id': scan_id})

    scan_status = 'Undefined'
    scan_duration = -1
    if khs_stop.count() == 1:
        scan_status = 'Done'
        scan_duration = khs_stop[0]['time'] - khs_start[0]['time']
    elif khs_stop.count() == 0:
        scan_status = 'Active'
        scan_duration = datetime.now() - khs_start[0]['time'] 

    scan_info = {
        'scan_id': scan_id,
        'time': khs_start[0]['time'],
        'duration': scan_duration,
        'status': scan_status,
        'result_no': mongo_db['kube_hunter'].count_documents({'scan_id': scan_id})
    }

    return scan_info

 
def kh_cluster_scans(scan_id):
    if type(scan_id).__name__ != 'ObjectId':
        scan_id = ObjectId(scan_id)

    mongo_c = MongoClient(conf['database']['connection'])
    mongo_db = mongo_c[conf['database']['dbname']]

    khs_results = mongo_db['kube_hunter'].find({'scan_id': scan_id})

    cluster_scans = []
    for khs in khs_results:
        cluster_scans.append(khs)

    return cluster_scans 

