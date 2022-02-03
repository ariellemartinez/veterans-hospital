import unicodedata
import re
import requests
import pandas as pd

def slugify(value, allow_unicode=False):
	# Taken from https://github.com/django/django/blob/master/django/utils/text.py
	value = str(value)
	if allow_unicode:
		value = unicodedata.normalize("NFKC", value)
	else:
		value = unicodedata.normalize("NFKD", value).encode(
			"ascii", "ignore").decode("ascii")
	value = re.sub(r"[^\w\s-]", "", value.lower())
	return re.sub(r"[-\s]+", "-", value).strip("-_")

counties = ["Nassau", "Suffolk"]

# We are defining the Socrata datasets we want to scrape here.
datasets = [
	{
		"identifier": "ptds-r8im",
		# "title": "Veterans Health Administration Timely and Effective Care Data",
		# "dataset_link": "https://data.cms.gov/provider-data/dataset/ptds-r8im",
		"description": "Quality measures for Northport VA Medical Center"
	}, {
		"identifier": "6qxe-iqz8",
		# "title": "Veterans Health Administration Behavioral Health Data",
		# "dataset_link": "https://data.cms.gov/provider-data/dataset/6qxe-iqz8",
		"description": "Behaviorial health measures for Northport VA Medical Center"
	} 
]

# We are going to call every item within "datasets" a "dataset". As we go through each dataset, we are going to scrape the dataset.
for dataset in datasets:
	try:
		# We are creating an empty list called "results".
		results = []
		# We are going to call every item within "counties" a "county". As we go through each county, we are going to scrape the dataset for that county.
		for county in counties:
			url = "https://data.cms.gov/provider-data/api/1/datastore/query/" + dataset["identifier"] + "/0"
			# The limit can be up to 500.
			limit = 500
			# Start the offset at 0.
			offset = 0
			initial_payload = "limit=" + str(limit) + "&offset=" + str(offset) + "&count=true&results=true&schema=true&keys=true&format=json&rowIds=false&conditions%5B0%5D%5Bproperty%5D=state&conditions%5B0%5D%5Boperator%5D=%3D&conditions%5B0%5D%5Bvalue%5D=NY&conditions%5B1%5D%5Bproperty%5D=county_name&conditions%5B1%5D%5Boperator%5D=%3D&conditions%5B1%5D%5Bvalue%5D=" + county
			# "requests" documentation page is here: https://docs.python-requests.org/en/master/user/quickstart/
			initial_request = requests.get(url, params=initial_payload)
			# As we go through each page of the dataset, we are going to scrape that page of the dataset.
			count = initial_request.json()["count"]
			i = 0
			while i < count / limit:
				offset = i * limit
				loop_payload = "limit=" + str(limit) + "&offset=" + str(offset) + "&count=true&results=true&schema=true&keys=true&format=json&rowIds=false&conditions%5B0%5D%5Bproperty%5D=state&conditions%5B0%5D%5Boperator%5D=%3D&conditions%5B0%5D%5Bvalue%5D=NY&conditions%5B1%5D%5Bproperty%5D=county_name&conditions%5B1%5D%5Boperator%5D=%3D&conditions%5B1%5D%5Bvalue%5D=" + county
				loop_request = requests.get(url, params=loop_payload)
				for result in loop_request.json()["results"]:
					results.append(result)
				i += 1
		# "pandas" documentation page is here: https://pandas.pydata.org/docs/index.html
		df = pd.DataFrame(results)
		file_name = slugify(dataset["description"])
		df.to_csv("csv/" + file_name + ".csv", index=False)
	except:
		pass