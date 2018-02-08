#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Create JIRA from ITSM
# written by: Erick Capote
# Product Development R&D


import sys

import base64
import ConfigParser
import logging
import time
import datetime
import helper_class
import requests
from bs4 import BeautifulSoup
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

### Make UTF8 the default encoding in script
reload(sys)
sys.setdefaultencoding('utf8')

# Define INI file
settings = ConfigParser.ConfigParser()
settings.read('./config.ini')


### SETUP THE FUNCTION FOR TO READ THE CONFIG FILE HEADERS
def ConfigSectionMap(section):
    dict1 = {}
    options = settings.options(section)
    for option in options:
        try:
            dict1[option] = settings.get(section, option)
            if dict1[option] == -1:
                DebugPrint("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1


def setup_custom_logger(name):
    LOG_FILENAME = './jira_itsm_with_SVR.log'
    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')
    handler = logging.FileHandler(LOG_FILENAME, mode='a')
    handler.setFormatter(formatter)
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return logger


def get_jira_eesc_tickets(base_url,username,pwd):
    try:
        url = base_url+'/search?jql=project=EESC&fields=id,key,customfield_10031&maxResults=1000'
        headers = {'Content-Type': 'application/json'}
        my_api_obj = helper_class.make_api_call()
        response_dict = my_api_obj.make_get_call(url, username, pwd, headers)
        logger.info('jira_response_dict: %s' % response_dict)
        # api_request = requests.get(url, auth=(username, pwd), headers=headers, verify=False)
        # api_response = api_request.json()
        # response_dict[api_request.status_code] = api_response
        # return response_dict
        return response_dict
    except Exception as e:
        return e


def get_today_itsm_incidents(base_url, date_1, date_2, itsm_user, itsm_pwd, itsm_sysparm_limit):
    try:
        url = base_url + '/api/now/table/incident?sysparm_limit='+itsm_sysparm_limit+'&sysparm_display_value=true&assignment_group=ITaaS.RD.IaaS&sysparm_query=opened_atBETWEENjavascript%3Ags.dateGenerate(%27' + date_1 + '%27%2C%2700%3A00%3A00%27)%40javascript%3Ags.dateGenerate(%27' + date_2 + '%27%2C%2723%3A59%3A59%27)'
        logger.info('API URL: %s' % url)
        headers = {'Content-Type': 'application/json'}
        my_api_obj = helper_class.make_api_call()
        response_dict = my_api_obj.make_get_call(url, itsm_user, itsm_pwd, headers)
        # api_request = requests.get(url, auth=(itsm_user, itsm_pwd), headers=headers, verify=False)
        logger.info('get_today_itsm_incidents_status_code: %s' % response_dict.keys())
        logger.info('get_today_itsm_incidents: %s' % response_dict)
        # api_response = api_request.json()
        return response_dict
    except Exception as e:
        return e


def get_today_itsm_svr(base_url, date_1, date_2, itsm_user, itsm_pwd, itsm_sysparm_limit):
    try:
        response_dict = {}
        url = base_url + '/api/now/table/u_request?sysparm_limit='+itsm_sysparm_limit+'&sysparm_display_value=true&assignment_group=ITaaS.RD.IaaS&sysparm_query=u_submitted_onBETWEENjavascript%3Ags.dateGenerate(%27' + date_1 +'%27%2C%2700%3A00%3A00%27)%40javascript%3Ags.dateGenerate(%27' + date_2 + '%27%2C%2723%3A59%3A59%27)'
        logger.info('API URL: %s' % url)
        headers = {'Content-Type': 'application/json'}
        my_api_obj = helper_class.make_api_call()
        response_dict = my_api_obj.make_get_call(url, itsm_user, itsm_pwd, headers)
        return response_dict
    except Exception as e:
        return e


def get_today_itsm_evt(base_url, date_1, date_2, itsm_user, itsm_pwd, itsm_sysparm_limit):
    try:
        url = base_url + '/api/now/table/u_rim_event?sysparm_limit='+itsm_sysparm_limit+'&sysparm_display_value=true&assignment_group=ITaaS.RD.ProdEng.Systems&sysparm_query=u_submitted_onBETWEENjavascript%3Ags.dateGenerate(%27' + date_1 +'%27%2C%2700%3A00%3A00%27)%40javascript%3Ags.dateGenerate(%27' + date_2 + '%27%2C%2723%3A59%3A59%27)'
        # logger.info('API URL: %s' % url)
        headers = {'Content-Type': 'application/json'}
        # api_request = requests.get(url, auth=(itsm_user, itsm_pwd), headers=headers, verify=False)
        # api_response = api_request.json()
        my_api_obj = helper_class.make_api_call()
        response_dict = my_api_obj.make_get_call(url, itsm_user, itsm_pwd, headers)
        return response_dict
    except Exception as e:
        return e


def make_jira_api_call(my_subject, description, case_no, jira_user, jira_pwd, base_url):
    response_dict = {}
    url = base_url+'/issue/'
    logger.info('jira_api_url: %s' % url)
    headers = {'Content-Type': 'application/json'}
    payload = '''{
    "fields": {
       "project":
       {
          "id": "10084"
       },
       "summary": "%s",
       "description": "%r",
       "issuetype": {
          "name": "Case Escalation"
       },
        "customfield_10031": "%s",
        "customfield_10032": [{
            "value":"New"
            }]
   }
   }''' % (my_subject, description, case_no)
    logger.info('jira_api_payload: %s' % payload)
    api_request = requests.post(url, auth=(jira_user, jira_pwd), headers=headers, data=payload, verify=False)
    api_response = api_request.json()
    logger.info('jira_api_status_code: %s' % api_request.status_code)
    logger.info('jira_api_text_response: %s' % api_request.text)
    response_dict[api_request.status_code] = api_response
    return response_dict


def process_jira_info(response):
    jira_search_dict = {}
    jira_issues = response['issues']
    if isinstance(jira_issues, dict):
        pass
    elif isinstance(jira_issues, list):
        for no_issues in xrange(len(jira_issues)):
            jira_search_dict_info = {}
            if 'fields' in response['issues'][no_issues].keys():
                jira_case_no = response['issues'][no_issues]['key']
                jira_search_dict_info['hyperlink_to_case'] = response['issues'][no_issues]['self']
                jira_search_dict_info['itsm_case_no'] = response['issues'][no_issues]['fields']['customfield_10031']
            else:
                jira_case_no = response['issues'][no_issues]['key']
                jira_search_dict_info['hyperlink_to_case'] = response['issues'][no_issues]['self']
            jira_search_dict[jira_case_no] = jira_search_dict_info
    logger.info('jira_search_dict: %s' % jira_search_dict)
    return jira_search_dict


def chk_jira_created(case_no_to_search, jira_dict):
    flag = 'false'
    jira_cases = []
    logger.info('Case to Search in Created Jira Func: %s' % case_no_to_search)
    for k, v in jira_dict.iteritems():
        if 'itsm_case_no' in jira_dict[k]:
            if jira_dict[k]['itsm_case_no'] is not None:
                jira_cases.append(jira_dict[k]['itsm_case_no'].encode('utf-8').lstrip().rstrip())
    logger.info('jira_cases: %s' % jira_cases)
    if case_no_to_search in jira_cases:
        flag = 'true'
        logger.info('We got a case match: %s' % case_no_to_search)
        logger.info('We got a case match Flag: %s' % flag)
    else:
        flag = 'false'
        logger.info('No match for: %s' % case_no_to_search)
        logger.info('No match flag: %s' % flag)
    return flag


def process_itsm_info(itsm_tickets):
    data = itsm_tickets
    logger.info('itsm_tickets: %s' % itsm_tickets)
    itsm_dict = {}
    for incident in data.iteritems():
        for no_of_incidents in xrange(len(incident[1])):
            itsm_dict_info = {}
            itsm_incident_no = incident[1][no_of_incidents]['number']
            itsm_dict_info['opened_at'] = incident[1][no_of_incidents]['opened_at']
            itsm_dict_info['assignment_group'] = incident[1][no_of_incidents]['assignment_group']['display_value']
            itsm_dict_info['state'] = incident[1][no_of_incidents]['state']
            itsm_dict_info['sys_updated_on'] = incident[1][no_of_incidents]['sys_updated_on']
            itsm_dict_info['short_description'] = incident[1][no_of_incidents]['short_description']
            itsm_dict_info['comments'] = incident[1][no_of_incidents]['comments'].encode('utf-8','ignore')
            logger.info('itsm_incident_no %s' % str(itsm_incident_no))
            logger.info('short_description %s' % incident[1][no_of_incidents]['short_description'])
            itsm_dict[itsm_incident_no] = itsm_dict_info
    return itsm_dict


def create_jira(itsm_dict, jira_base_url):
    for k, v in itsm_dict.iteritems():
        case_no_to_search = k
        logger.info('Case To Search? %s' % str(case_no_to_search))
        is_jira_created = chk_jira_created(case_no_to_search, jira_dict)
        logger.info('Is Jira Created? %s' % str(is_jira_created))
        if 'false' in is_jira_created:
            case_no_to_search = k
            my_subject = (v['short_description']).encode('utf8')
            title_raw = str(case_no_to_search + ' | ' + my_subject)
            title = title_raw.replace('\"',"")
            logger.info('my_subject: %s' % my_subject)
            # work_notes = v['work_notes']
            cleansed_work_notes = v['comments'].replace('\"', " ")
            cleansed_work_notes_2 = cleansed_work_notes.replace("\xc2\xa0","")
            soup = BeautifulSoup(cleansed_work_notes_2,'html.parser')
            # description = cleansed_work_notes_2[:100]
            description = soup
            # logger.info('description: %s' % description)
            result = make_jira_api_call(title, description, case_no_to_search, jira_user, jira_pwd, jira_base_url)
            logger.info('MAKE_JIRA_API: %s' % result.keys())
            if 400 in result.keys():
                description2 = title.replace("'","")
                result = make_jira_api_call(title, description2, case_no_to_search, jira_user, jira_pwd, jira_base_url)
                logger.info('RE_TRY_MAKE_JIRA: %s' % result)
                if 400 in result.keys():
                    description2 = case_no_to_search
                    title = case_no_to_search
                    result = make_jira_api_call(title, description2, case_no_to_search, jira_user, jira_pwd,
                                                jira_base_url)
                    logger.info('2ND_JIRA_TRY: %s' % result)
            # logger.info('WORK_NOTES: %s' % v['work_notes'])
            return result
        else:
            logger.info('CASE ALREADY CREATED IN JIRA')



## Set the 60 day interval to use to get ITSM tickets
itsm_date_interval = int(ConfigSectionMap('itsm_info')['itsm_date_interval'])
today = datetime.date.today()
date_diff = datetime.timedelta(days=itsm_date_interval)
date_2 = time.strftime('%Y/%m/%d')
date_1 = (today - date_diff).strftime('%Y/%m/%d')

## set empty variable --- why?
case_no_to_search = ''

## Specify JIRA info
jira_user = ConfigSectionMap('jira_info')['jira_user'].strip("'")
jira_pwd = ConfigSectionMap('jira_info')['jira_pwd'].strip("'")
jira_base_url = ConfigSectionMap('jira_info')['jira_base_url'].strip("'")

## ITSM Log-in info
itsm_user = base64.b64decode(ConfigSectionMap('itsm_info')['itsm_username'].strip("'"))
itsm_pwd = base64.b64decode(ConfigSectionMap('itsm_info')['itsm_pwd'].strip("'"))
itsm_base_url = ConfigSectionMap('itsm_info')['itsm_base_url'].strip("'")
itsm_sysparm_limit = ConfigSectionMap('itsm_info')['itsm_sysparm_limit'].strip("'")

## instantiate logger
logger = setup_custom_logger('jira_itsm')


## API Call to get last 1000 JIRA tickets created
get_jira_tickets = get_jira_eesc_tickets(jira_base_url,jira_user,jira_pwd)
# print get_jira_tickets
if 200 in get_jira_tickets.keys():
    jira_dict = process_jira_info(get_jira_tickets[200])

else:
    logger.info('ERROR conn to JIRA_API %r' % get_jira_tickets)
    # print get_jira_tickets


## Get ICM Tickets API ###
itsm_incident_tickets = get_today_itsm_incidents(itsm_base_url, date_1, date_2, itsm_user, itsm_pwd, itsm_sysparm_limit)
if 200 in itsm_incident_tickets.keys():
    itsm_incident_dict = process_itsm_info(itsm_incident_tickets[200])
    logger.info('itsm_incident_dict %r' % itsm_incident_dict)
    ## Create ICM JIRA
    new_jira_result = create_jira(itsm_incident_dict, jira_base_url)
else:
    logger.info('ITSM ERROR %r' % itsm_incident_tickets)


## GET SVR Tickets
itsm_svr_tickets = get_today_itsm_svr(itsm_base_url, date_1, date_2, itsm_user, itsm_pwd, itsm_sysparm_limit)
# itsm_svr_dict = process_itsm_info(itsm_svr_tickets)
# logger.info('itsm_svr_dict %r' % itsm_svr_dict)
if 200 in itsm_svr_tickets.keys():
    itsm_svr_dict = process_itsm_info(itsm_svr_tickets[200])
    logger.info('itsm_svr_dict %r' % itsm_svr_dict)
    ## Create SVR JIRA`
    create_jira(itsm_svr_dict, jira_base_url)

else:
    logger.info('ERROR GETTING SVR TICKETS FROM ITSM!!!!!!')


######################### NOT USED DUE TO VOLUME ################
## GET EVT Tickets
# itsm_evt_tickets = get_today_itsm_evt(itsm_base_url, date_1, date_2, itsm_user, itsm_pwd, itsm_sysparm_limit)
# itsm_evt_dict = process_itsm_info(itsm_evt_tickets)
# logger.info('itsm_evt_dict %r' % itsm_evt_dict)

## Create EVT JIRA
# create_jira(itsm_evt_dict, create_jira)
