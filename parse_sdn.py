"""
Parse the OFAC SDN list"

The OFAC list is given as xml.
Each entity is recorded as a "DistinctParty"
Each DistinctParty entry is formatted like this

DistinctParty
	NamePartValue
	NamePartValue
	....
	VersionDetail
	VersionDetail
	....
	DatePeriod
		Start
			From 
				Year
				Month
				Day
			To
				Year
				Month
				Day
		End
			From
				Year
				Month
				Day
			To
				Year
				Month
				Day

For cryptocurrency addresses, the address is in the VersionDetail field

The script writes the list to the file "parsed_sdn.csv"
"""


import lxml
import cchardet
from bs4 import BeautifulSoup
import re
import requests
import os
from datetime import datetime
import pandas as pd

xmlfile = "sdn_advanced.xml"

if not os.path.exists(xmlfile):
	url = "https://www.treasury.gov/ofac/downloads/sanctions/1.0/sdn_advanced.xml"
	print( f"Retrieving file: {url}" )
	r = requests.get(url, allow_redirects=True)
	open(xmlfile, 'wb').write(r.content)

with open(xmlfile, 'r') as f:
	data = f.read()

soup = BeautifulSoup(data, features="xml" )

DP = soup.find_all('DistinctParty')

rows = []
for dp in DP:
	name_tags = dp.find_all("NamePartValue")
	names = [nt.text for nt in name_tags]
	vd_tags = dp.find_all("VersionDetail")
	ids = [vd.text for vd in vd_tags]
	ids = list(set(ids)) #Remove duplicates
	date_tags = dp.find_all("DatePeriod")
	if len(date_tags ) > 1:
		print( f"Error too many date periods ({len(date_tags)}) for {names}" )
	if len(date_tags) == 0: #Many entries have no dates
		for Id in ids:
			row = { 'detail': str(Id).rstrip(), 'names': ", ".join(names) }
			rows.append(row)
		continue

	date_period = date_tags[0]
	start_year = date_period.find('Start').find('From').find('Year').text
	start_month = date_period.find('Start').find('From').find('Month').text
	start_day = date_period.find('Start').find('From').find('Day').text
	start_year1 = date_period.find('Start').find('To').find('Year').text
	start_month1 = date_period.find('Start').find('To').find('Month').text
	start_day1 = date_period.find('Start').find('To').find('Day').text
	end_year = date_period.find('End').find('From').find('Year').text
	end_month = date_period.find('End').find('From').find('Month').text
	end_day = date_period.find('End').find('From').find('Day').text
	end_year1 = date_period.find('End').find('To').find('Year').text
	end_month1 = date_period.find('End').find('To').find('Month').text
	end_day1 = date_period.find('End').find('To').find('Day').text

	start0 = datetime.strptime(f"{start_year}-{start_month}-{start_day}","%Y-%m-%d")
	start1 = datetime.strptime(f"{start_year1}-{start_month1}-{start_day1}","%Y-%m-%d")
	end0 = datetime.strptime(f"{end_year}-{end_month}-{end_day}","%Y-%m-%d")
	end1 = datetime.strptime(f"{end_year1}-{end_month1}-{end_day1}","%Y-%m-%d")

	for Id in ids:
		row = { 'detail': str(Id).rstrip(), 'names': ", ".join(names), 'start0': start0, 'start1': start1, 'end0': end0, 'end1': end1 }
		rows.append(row)

df = pd.DataFrame(rows)
df.drop_duplicates(inplace=True)
df.to_csv('data/parsed_sdn.csv',index=False)

tornado = df[df.names.str.find('Tornado') >= 0]
tornado = tornado[tornado.detail.notna()]
tornado.to_csv('data/tornado_addresses.csv',index=False)


