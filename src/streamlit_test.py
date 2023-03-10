#!/usr/bin/env python
# coding: utf-8

import requests
import sys
import os
import pandas as pd
import io
import streamlit as st
from datetime import datetime, timedelta


st.header('Netztransparenz WebAPI Test')

# add your Client-ID and Client-secret from the API Client configuration GUI to
# your environment variable first
# IPNT_CLIENT_ID = os.environ.get('IPNT_CLIENT_ID')
IPNT_CLIENT_ID = st.text_input('IPNT_CLIENT_ID')
# IPNT_CLIENT_SECRET = os.environ.get('IPNT_CLIENT_SECRET')
IPNT_CLIENT_SECRET = st.text_input('IPNT_CLIENT_SECRET')

ACCESS_TOKEN_URL = "https://identity.netztransparenz.de/users/connect/token"


# Ask for the token providing above authorization data
response = requests.post(ACCESS_TOKEN_URL,
                data = {
                        'grant_type': 'client_credentials',
                        'client_id': IPNT_CLIENT_ID,
                        'client_secret': IPNT_CLIENT_SECRET
        })

# Parse the token from the response if the response was OK 
if response.ok:
    TOKEN = response.json()['access_token']
else:
    print(f'Error retrieving token\n{response.status_code}:{response.reason}',
        file = sys.stderr)
    exit(-1)

# Provide URL to request health info on API
myURL = "https://ds.netztransparenz.de/api/v1/health"
response = requests.get(myURL, headers = {'Authorization': 'Bearer {}'.format(TOKEN)})
print(response.text, file = sys.stdout)


end_datetime = datetime.now()
start_datetime = end_datetime-timedelta(days=3)
st.write(start_datetime, end_datetime)

DATA_TYPE = st.selectbox('Vermarktung', ['VermarktungExaa','VermarktungEpex', 'VermarktungsSonstige', 'VermarktungsSolar', 'VermarktungsWind'])

myURL = f"https://ds.netztransparenz.de/api/v1/data/vermarktung/{DATA_TYPE}/{start_datetime}/{end_datetime}"
response = requests.get(myURL, headers = {'Authorization': 'Bearer {}'.format(TOKEN)})

df = pd.read_csv(io.StringIO(response.content.decode('utf-8')), delimiter=';', decimal=',', thousands='.').sort_index(ascending=False)
df['datetime']=df.Datum+'T'+df.von+':00Z'
df.set_index('datetime', inplace=True)
df = df.drop(['Datum', 'von', 'Zeitzone von', 'bis', 'Zeitzone bis'], axis=1)

st.line_chart(df, y=['50Hertz (MW)', 'Amprion (MW)', 'TenneT TSO (MW)', ' TransnetBW (MW)'])
st.write(df)
