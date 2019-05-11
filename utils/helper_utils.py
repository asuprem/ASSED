import time
from datetime import datetime
import sys, os
import http.client as httplib, urllib.parse as urllib, json
import re

# Checks if two dictionaries are equal
# TODO optimize this
def dict_equal(d1, d2):
    """ return True if all keys and values are the same """
    flag1= True
    flag2= True
    for key in d1:
        if not (key in d2 and d1[key] == d2[key]):
            flag1 = False
    for key in d2:
        if not (key in d1 and d1[key] == d2[key]):
            flag2 = False
    return flag1 and flag2


#setu up PID for recurrence checks
def setup_pid(pid_name, logdir=None):
    import os, sys
    #pid_name will be application name -- '/path/app.py'
    pid = str(os.getpid())
    if logdir is None:
        pidFile = './logfiles/' + pid_name + '.pid'
    else:
        pidFile = os.path.join(logdir, pid_name + '.pid')

    if os.path.isfile(pidFile):
        print("pidfile already exists. exiting")
        sys.exit()
    open(pidFile,'w').write(pid)

def readable_time():
    return datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')

def std_flush(*args,**kwargs):
    print(" ".join(map(str,args)))
    sys.stdout.flush()

def location_standardize(location):
    """ Standardize by removing special characters and location stopwords. """
    temp_str = location_normalize(location)
    temp_lst = temp_str.split(" ")
    location_stopwords = ["island", "islands", "volcano", "de", "new", "northern", "southern"]
    temp_lst = [item for item in temp_lst if (item not in location_stopwords and len(item) > 5)]

    return ":".join(temp_lst)

def location_normalize(location):
    return re.sub('[^a-zA-Z0-9\n\.]', ' ',location.strip().lower())

def high_confidence_streamer_key(key_val):
    return "assed:hcs:" + key_val

def sublocation_key(key_val):
    return "assed:sublocation:"+key_val

def lookup_address_only(address, API_KEY):
    # So first we need to check if the location is in our database...
    host = 'maps.googleapis.com'
    params = {'address': address, 'key': API_KEY}
    url = '/maps/api/geocode/json?'+urllib.urlencode(params)
    req = httplib.HTTPSConnection(host)
    req.putrequest('GET', url)
    req.putheader('Host', host)
    req.endheaders()
    resp = req.getresponse()
    if resp.status==200:
        result = json.load(resp, encoding='UTF-8')
        if 'results' in result:
            results = result['results']
            if len(results) > 0:
                item = results[0]
                if 'geometry' in item:
                    geometry = item['geometry']
                    if 'location' in geometry:
                        location = geometry['location']
                        lat = location['lat']
                        lng = location['lng']
            else:
                return None, None
    else:
        return None, None
    return lat, lng

def generate_cell(N, E, coef=0.04166666666667):
    if coef<0.04166666666667: coef = 0.04166666666667
    if coef>1: coef = 1
    row = int(round((90.0+N)/coef))
    if row<0:
        raise ValueError
    col = int(round((180.0+E)/coef))
    key = str(row)+'_'+str(col)
    return key