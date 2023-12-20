#
# EMLinux CVE checker.
# Download and store NVD's CVE data
#
# Copyright (c) Cybertrust Japan Co., Ltd.
#
# SPDX-License-Identifier: MIT
#

import os
import sqlite3
import datetime
import urllib.request
import urllib.parse
import gzip
import http
import time
import json
import logging

CVE_DATABASE_NAME = "nvd_cve_db.db"

CVE_DB_UPDATE_INTERVAL = 86400

NVDCVE_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"
NVDCVE_API_KEY = None

logger = logging.getLogger("emlinux-cve-check")

def parse_node_and_insert(conn, node, cveId):

    def cpe_generator():
        for cpe in node.get('cpeMatch', ()):
            if not cpe['vulnerable']:
                return
            cpe23 = cpe.get('criteria')
            if not cpe23:
                return
            cpe23 = cpe23.split(':')
            if len(cpe23) < 6:
                return
            vendor = cpe23[3]
            product = cpe23[4]
            version = cpe23[5]

            if cpe23[6] == '*' or cpe23[6] == '-':
                version_suffix = ""
            else:
                version_suffix = "_" + cpe23[6]

            if version != '*' and version != '-':
                # Version is defined, this is a '=' match
                yield [cveId, vendor, product, version + version_suffix, '=', '', '']
            elif version == '-':
                # no version information is available
                yield [cveId, vendor, product, version, '', '', '']
            else:
                # Parse start version, end version and operators
                op_start = ''
                op_end = ''
                v_start = ''
                v_end = ''

                if 'versionStartIncluding' in cpe:
                    op_start = '>='
                    v_start = cpe['versionStartIncluding']

                if 'versionStartExcluding' in cpe:
                    op_start = '>'
                    v_start = cpe['versionStartExcluding']

                if 'versionEndIncluding' in cpe:
                    op_end = '<='
                    v_end = cpe['versionEndIncluding']

                if 'versionEndExcluding' in cpe:
                    op_end = '<'
                    v_end = cpe['versionEndExcluding']

                if op_start or op_end or v_start or v_end:
                    yield [cveId, vendor, product, v_start, op_start, v_end, op_end]
                else:
                    # This is no version information, expressed differently.
                    # Save processing by representing as -.
                    yield [cveId, vendor, product, '-', '', '', '']

    conn.executemany("insert into PRODUCTS values (?, ?, ?, ?, ?, ?, ?)", cpe_generator()).close()

def update_db(conn, elt):
    """
    Update a single entry in the on-disk database
    """

    accessVector = None
    vectorString = None
    cveId = elt['cve']['id']
    vulnStatus = elt['cve']['vulnStatus']
    cveDesc = ""
    for desc in elt['cve']['descriptions']:
        if desc['lang'] == 'en':
            cveDesc = desc['value']
    date = elt['cve']['lastModified']
    try:
        accessVector = elt['cve']['metrics']['cvssMetricV2'][0]['cvssData']['accessVector']
        vectorString = elt['cve']['metrics']['cvssMetricV2'][0]['cvssData']['vectorString']
        cvssv2 = elt['cve']['metrics']['cvssMetricV2'][0]['cvssData']['baseScore']
    except KeyError:
        cvssv2 = 0.0
    cvssv3 = None
    try:
        accessVector = accessVector or elt['cve']['metrics']['cvssMetricV30'][0]['cvssData']['attackVector']
        vectorString = vectorString or elt['cve']['metrics']['cvssMetricV30'][0]['cvssData']['vectorString']
        cvssv3 = elt['cve']['metrics']['cvssMetricV30'][0]['cvssData']['baseScore']
    except KeyError:
        pass
    try:
        accessVector = accessVector or elt['cve']['metrics']['cvssMetricV31'][0]['cvssData']['attackVector']
        vectorString = vectorString or elt['cve']['metrics']['cvssMetricV31'][0]['cvssData']['vectorString']
        cvssv3 = cvssv3 or elt['cve']['metrics']['cvssMetricV31'][0]['cvssData']['baseScore']
    except KeyError:
        pass
    accessVector = accessVector or "UNKNOWN"
    vectorString = vectorString or "UNKNOWN"
    cvssv3 = cvssv3 or 0.0

    conn.execute("insert or replace into NVD values (?, ?, ?, ?, ?, ?, ?, ?)",
                [cveId, vulnStatus, cveDesc, cvssv2, cvssv3, date, accessVector, vectorString]).close()

    try:
        for config in elt['cve']['configurations']:
            # This is suboptimal as it doesn't handle AND/OR and negate, but is better than nothing
            for node in config["nodes"]:
                parse_node_and_insert(conn, node, cveId)
    except KeyError:
            logger.debug("CVE %s has no configurations" % cveId)

def nvd_request_next(url, api_key, args):
    """
    Request next part of the NVD dabase
    """

    request = urllib.request.Request(url + "?" + urllib.parse.urlencode(args))
    if api_key:
        request.add_header("apiKey", api_key)
    logger.debug(f"Requesting {request.full_url}")

    for attempt in range(5):
        try:
            r = urllib.request.urlopen(request)

            if (r.headers['content-encoding'] == 'gzip'):
                buf = r.read()
                raw_data = gzip.decompress(buf)
            else:
                raw_data = r.read().decode("utf-8")

            r.close()
        except Exception as e:
            logger.debug(f"CVE database: received error ({e}), retrying")
            time.sleep(6)
            pass
        else:
            return raw_data
    else:
        # We failed at all attempts
        return None

def fetch_all_cves(db_file, conn, last_modified, api_key):

    index = 0
    url = NVDCVE_URL

    req_args = {}

    if last_modified is not None:
        req_args["lastModStartDate"] = last_modified
        req_args["lastModEndDate"] = datetime.datetime.now().isoformat()

    # Recommended by NVD
    sleep_time = 6
    if api_key:
        sleep_time = 2

    with open(db_file, 'a') as cve_f:
        while True:
            logger.debug("Updating entries")

            req_args["startIndex"] = index

            raw_data = nvd_request_next(url, api_key, req_args)
            if raw_data is None:
                return False

            data = json.loads(raw_data)

            index = data["startIndex"]
            total = data["totalResults"]
            per_page = data["resultsPerPage"]
            logger.debug(f"Got {per_page} entries")
            for cve in data["vulnerabilities"]:
               update_db(conn, cve)

            index += per_page
            if index >= total:
               break

            time.sleep(sleep_time)

    return True

def update_last_modified_date(conn):
    d = datetime.datetime.now().isoformat()

    with conn:
        c = conn.cursor()

        cursor = c.execute("SELECT LASTMODIFIED from META where ID=1")
        last = cursor.fetchone()

        if last is None:
            sql = f"INSERT INTO META VALUES (1, '{d}')"
        else:
            sql = f"UPDATE META set LASTMODIFIED='{d}' where ID=1"

        c.execute(sql)

        c.close()


def get_last_modified_date(conn):
    with conn:
        c = conn.cursor()

        cursor = c.execute("SELECT LASTMODIFIED from META")

        last = cursor.fetchone()
        c.close()

        if last is None:
            return None

        return last[0]

def initialize_nvd_cve_db(conn):
    with conn:
        c = conn.cursor()

        c.execute("CREATE TABLE IF NOT EXISTS META (ID NUMBER UNIQUE, LASTMODIFIED TEXT)")

        c.execute("CREATE TABLE IF NOT EXISTS NVD (ID TEXT UNIQUE, VULNSTATUS TEXT, SUMMARY TEXT, SCOREV2 TEXT, \
            SCOREV3 TEXT, MODIFIED INTEGER, VECTOR TEXT, VECTORSTRING TEXT)")

        c.execute("CREATE TABLE IF NOT EXISTS PRODUCTS (ID TEXT, \
            VENDOR TEXT, PRODUCT TEXT, VERSION_START TEXT, OPERATOR_START TEXT, \
            VERSION_END TEXT, OPERATOR_END TEXT)")

        c.execute("CREATE INDEX IF NOT EXISTS PRODUCT_ID_IDX on PRODUCTS(ID);")

        c.close()

def update_nvd_db(dl_dir, nvd_api_key):
    db_file = f"{dl_dir}/{CVE_DATABASE_NAME}"

    conn = sqlite3.connect(db_file)
    logger.debug(f"Initialize nvd cve database {db_file}")
    initialize_nvd_cve_db(conn)

    last_modified = get_last_modified_date(conn)
    skip_db_update = False

    logger.info("Update NVD CVE database")
    if last_modified:
        d1 = datetime.datetime.fromisoformat(datetime.datetime.now().isoformat())
        d2 = datetime.datetime.fromisoformat(last_modified)

        date_delta = d1 - d2
        if date_delta.total_seconds() < CVE_DB_UPDATE_INTERVAL:
            skip_db_update = True
            logger.info(f"Last database update is in 1day so skip NVD database update")
        else:
            # Database is too old so that fetch all data
            if date_delta.days > 120:
                last_modified = None

    if not skip_db_update:
        if not fetch_all_cves(db_file, conn, last_modified, nvd_api_key):
            return None

        logger.info("Update last modified date")
        if update_last_modified_date(conn):
            conn.commit()

    conn.close()

    return db_file
