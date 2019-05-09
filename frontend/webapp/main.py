import yaml
import logging

from datetime import datetime
from flask import Flask, render_template
from pymongo import MongoClient, DESCENDING 

import lib.scanner.controller as a_s_c
import lib.management.controller as a_m_c

app = Flask(__name__, static_url_path='/static')

KUBE_SCAR_WEB_CONF='/app/config.yaml'
conf = yaml.safe_load(open(KUBE_SCAR_WEB_CONF))
 
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=10
)

@app.route("/")
def index():
    return render_template('index.html')
 
@app.route("/scanner/kube-hunter")
def scanner_kube_hunter():
    scans_info = a_s_c.kh_scans()
    
    logging.debug(scans_info)

    return render_template('/scanner/kube-hunter.html', scans=scans_info)
 
@app.route("/scanner/kube-hunter/scan/<scan_id>")
def scanner_kube_hunter_scan(scan_id = None):
    if scan_id == None:
        return render_template('http_status_codes/404.html'), status.HTTP_404_NOT_FOUND

    scan_info = a_s_c.kh_scan_info(scan_id)
    clusters_scan_info = a_s_c.kh_cluster_scans(scan_id)

    return render_template('/scanner/kube-hunter-scan.html', scan=scan_info, clusters=clusters_scan_info)

@app.route("/cloud/google-cloud")
def cloud_google_cloud():
    return render_template('/cloud/google-cloud.html')

@app.route("/management/")
def management():
    commands = a_m_c.commands()

    return render_template('/management/index.html', commands=commands)

@app.route("/management/command/type/<command_type>")
def management_command_run(command_type = None):
    if command_type == None:
        return render_template('http_status_codes/404.html'), status.HTTP_404_NOT_FOUND

    return render_template('/management/command_run.html', command_type=command_type)

@app.route("/documentation/")
def documentation():
    return render_template('/documentation/index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
