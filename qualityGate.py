import sys
import argparse
import os.path
import json
import requests

# REST API Endpoints
API_ENDPOINT_TIMESERIES = "/api/v1/timeseries"

# HTTP Methods when calling the Dynatrace API via queryDynatraceAPIEx
HTTP_GET = "GET"
HTTP_POST = "POST"
HTTP_PUT = "PUT"
HTTP_DELETE = "DELETE"

# VIOLATION_ACTION
VIOLATION_ACTION_WARNING = 1
VIOLATION_ACTION_FAIL = 2

# Monitoring as Code (monspec) CONSTANTS
MONSPEC_PERFSIGNATURE = "perfsignature"
MONSPEC_PERFSIGNATURE_TIMESERIES = "timeseries"
MONSPEC_PERFSIGNATURE_AGGREGATE = "aggregate"
MONSPEC_PERFSIGNATURE_SMARTSCAPE = "smartscape"
MONSPEC_PERFSIGNATURE_METRICID = "metricId"
MONSPEC_PERFSIGNATURE_METRICDEF = "metricDef"
MONSPEC_PERFSIGNATURE_SOURCE = "source"
MONSPEC_PERFSIGNATURE_COMPARE = "compare"
MONSPEC_PERFSIGNATURE_THRESHOLD = "threshold"
MONSPEC_PERFSIGNATURE_RESULT = "result"
MONSPEC_PERFSIGNATURE_RESULT_COMPARE = "result_compare"
MONSPEC_PERFSIGNATURE_UPPERLIMIT = "upperlimit"
MONSPEC_PERFSIGNATURE_LOWERLIMIT = "lowerlimit"

MONSPEC_DISPLAYNAME = "displayName"

MONSPEC_METRICTYPE_SERVICE = "Monspec Service Metric"
MONSPEC_METRICTYPE_SMARTSCAPE = "Monspec Smartscape Metric"


# Returns the Authentication Header for the Dynatrace REST API
def getAuthenticationHeader(token):
    return {"Authorization": "Api-Token " + token}


def queryDynatraceAPI(httpMethod, apiEndpoint, queryString, postBody):

    print("DEBUG - queryDynatraceAPIEx: " + apiEndpoint + "?" + queryString + " - BODY: " + str(postBody))

    jsonContent = None
    myResponse = None
    if httpMethod == HTTP_GET:
        myResponse = requests.get(DT_URL, headers=getAuthenticationHeader(DT_TOKEN), verify=False)

    # For successful API call, response code will be 200 (OK)
    if (myResponse.ok):
        if (len(myResponse.text) > 0):
            jsonContent = json.loads(myResponse.text)

    else:
        jsonContent = json.loads(myResponse.text)
        errorMessage = ""
        if jsonContent["error"]:
            errorMessage = jsonContent["error"]["message"]
            print("Dynatrace API returned an error: " + errorMessage)
        jsonContent = None
        raise Exception("Error", "Dynatrace API returned an error: " + errorMessage)

    return jsonContent

def getAttributeOrDefault(baseobject, attributename, default):
    "Tries to get the attribute with that name from that object or returns default if not existing"
    attributeValue = getAttributeOrNone(baseobject, attributename)
    if attributeValue is None:
        attributeValue = default
    return attributeValue


def getAttributeOrNone(baseobject, attributename):
    "Tries to get the attribute with that name from that object or returns None if not existing"
    attributeValue = None
    try:
        attributeValue = baseobject[attributename]
    except:
        attributeValue = None
    return attributeValue

def readFile(theFile):
    jsonFromFile = None

    with open(theFile) as json_data:
        jsonFromFile = json.load(json_data)

    return jsonFromFile


def process():
    monspecJson = readFile(MONSPEC_FILE)
    performanceSignatureJson = readFile(PERFSIG_FILE)

    print('====================================================')
    print('Gate Test')
    print('====================================================')
    if VIOLATION_ACTION == VIOLATION_ACTION_WARNING:
        print('just a warning')
    else:
        print('you failed')
        exit(1)


# python qualityGate.py -m monspec/carts_monspec.json -p monspec/carts_perfsig.json -i monspec/carts_pipelineinfo.json -u https://<TENTANT>.live.dynatrace.com -t <TOKEN>
if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-m", "--monspec", required=True, help="name of the monspec file")
    ap.add_argument("-p", "--perfsig", required=True, help="name of the perfsig file")
    ap.add_argument("-u", "--url", required=True, help="Dynatrace tenant URL")
    ap.add_argument("-t", "--token", required=True, help="Dynatrace API token")
    ap.add_argument("-a", "--action", default=1, help="violation action. 1=warning only (default), 2=fail")
    args = vars(ap.parse_args())

    MONSPEC_FILE = args["monspec"]
    PERFSIG_FILE = args["perfsig"]
    VIOLATION_ACTION = args["action"]
    DT_URL = args["url"]
    DT_TOKEN = args["token"]

    if not os.path.isfile(MONSPEC_FILE):
        print('Error: MONSPEC file not found: ' + MONSPEC_FILE)
        exit(1)
    if not os.path.isfile(PERFSIG_FILE):
        print('Error: PERFSIG file not found: ' + PERFSIG_FILE)
        exit(1)
    if VIOLATION_ACTION not in [VIOLATION_ACTION_FAIL, VIOLATION_ACTION_WARNING]:
        print('Error: ACTION must have a value of 1 or 2')
        exit(1)
    if not DT_URL.startswith("https://"):
        print('Error: Dynatrace URL must start with https://')
        exit(1)

    process()


