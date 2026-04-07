#!/usr/bin/env python3

from pprint import pprint as pp
import requests
import logging
import hashlib
import json
import time

#logging.basicConfig(level=logging.DEBUG)
app_key = r'73858910-710d-476b-b664-8cab42e10f3c'
launch_request_data = {
    "player_id": "7795951",
    "player_name": "254798347957",
    "player_token": "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIyNTQ3OTgzNDc5NTciLCJpYXQiOjE3MzgxMzk3MzEsImV4cCI6MTczODIyNjEzMX0.Rr9LFNR3-PX2z1gNLS2NJ8ybODmteihXE3ZooDm5W9Q",
    "game_uuid": "gfhjdghvfdvsaddd",
    "currency": "KES",
    "demo": 0
}

def md5(s):
    return hashlib.md5(s.encode()).hexdigest()

def sort_nested_array(array):
    """
    Recursively sorts a nested dictionary or list by key.
    """
    if isinstance(array, dict):
        sorted_array = {}
        for key in sorted(array.keys()):
            value = array[key]
            if isinstance(value, (dict, list)):  # Recursive case for nested structures
                sorted_array[key] = sort_nested_array(value)
            else:
                sorted_array[key] = value
        return sorted_array
    elif isinstance(array, list):
        return [sort_nested_array(item) if isinstance(item, (dict, list)) else item for item in array]
    else:
        return array

def hash_create(request, token_key):
    """
    Creates a hash from the given request (which is a dictionary) and tokenKey.
    """
    hashkey = ''

    # Ensure the request is a dictionary
    if isinstance(request, dict):
        request = sort_nested_array(request)  # Sort the nested arrays/dictionaries
        for key, value in sorted(request.items()):
            if isinstance(value, (dict, list)):  # Handle nested dictionaries or lists
                for key_val, val in value.items():
                    hashkey += f"&{key_val}={hashlib.md5(json.dumps(val, sort_keys=True).encode('utf-8')).hexdigest()}"
                continue
            hashkey += f"&{key}={value}"

    hashkey = hashkey.lstrip('&')
    return hashlib.md5((hashkey + token_key).encode('utf-8')).hexdigest()

def make_signature(d, k):
    payload = d
    app_key = k
    hashed_value = hash_create(payload, app_key)
    return hashed_value

def test_games_url():
    url = "https://api.staging.betkraft.co.uk/v1/games"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "x-api-key": r'B//J+KLsDtk9XMT9ZHDHxvy3.075fT6YHOowfNYHmrqKAo41E6QwxvWezkqVAEH8bvbLffaLyiv',
        "x-signature-key": md5(app_key),
        "x-timestamp": str(int(time.time()))
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        print("Games URL Response:", response.json())
    except requests.exceptions.RequestException as e:
        print("Games URL Request Failed:", e)

def test_launch_url(d):
    url = "https://api.staging.betkraft.co.uk/v1/launch"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "x-api-key": r'B//J+KLsDtk9XMT9ZHDHxvy3.075fT6YHOowfNYHmrqKAo41E6QwxvWezkqVAEH8bvbLffaLyiv',
        "x-signature-key": make_signature(d, app_key),
        "x-timestamp": str(int(time.time()))
    }
    try:
        response = requests.post(url, json=d, headers=headers)
        response.raise_for_status()
        print("Launch URL Response:", response.json())
    except requests.exceptions.RequestException as e:
        print("Launch URL Request Failed:", e)


test_games_url()
test_launch_url(launch_request_data)

