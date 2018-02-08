#!/usr/bin/env python
# -*- coding: utf-8 -*-
# API calls helper class
# written by: Erick Capote

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class make_api_call(object):
    ''' API class to help make API calls with the request package'''

    def __init__(self):
        ''' declare global variables for class'''
        # self.url = url
        # self.usr = usr
        # self.pwd = pwd
        # self.headers = {'Content-Type': 'application/json'}

    def make_get_call(self, url, usr, pwd, headers):
        response_dict = {}
        # headers = {'Content-Type': 'application/json'}
        api_request = requests.get(url, auth=(usr, pwd), headers=headers, verify=False)
        api_response = api_request.json()
        response_dict[api_request.status_code] = api_response
        return response_dict

    def make_post_call(self, url, usr, pwd, headers, payload):
        # headers = {'Content-Type': 'application/json'}
        response_dict = {}
        api_request = requests.post(url, auth=(usr, passwd), headers=headers, data=payload, verify=False)
        api_response = api_request.json()
        response_dict[api_request.status_code] = api_response
        return response_dict
