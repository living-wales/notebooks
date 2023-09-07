from datetime import datetime, timedelta
from hashlib import sha256
import os
import requests

webhook_token   = os.environ['WEBHOOK_KEY']
webhook_host    = 'http://service.livingwales.space'
action_name     = 'refresh-repo'
action_args     = []

time = datetime.utcnow()
time = time - timedelta(seconds=time.second, microseconds=time.microsecond)
auth_token = sha256('{};{}'.format(webhook_token, time.isoformat()).encode('utf-8')).hexdigest()
auth_header = {'Authorization': 'token {}'.format(auth_token)}

url = '{}/webhook/action/{}/{}'.format(webhook_host, action_name, '/'.join(str(a) for a in action_args))
response = requests.get(url,headers=auth_header)

if response.status_code == 200:
    response_json = response.json()

    print(response_json)
    print('SUCCESS: Request the status file at {}/webhook/status/{}'.format(webhook_host, response_json['action_id']))
else:
    print('ERROR: Webhook responded with status code {}'.format(response.status_code))