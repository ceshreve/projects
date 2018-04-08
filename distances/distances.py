import urllib.request
import urllib.parse
import json

######## Settings ########

# Verbose
# 	prints distance between each central location
# 	and and each evaluation point
# 	when False, does not print "Distance from x to y = z"
#	default: True

verbose = True

# Central location summary
#	prints the numbers of places meeting criteria
#	from each central location
#	when False, does not print "x is less than c from d places:"
#	default: True

summary = True

# Evaluation locations
#	name of file containing json list of key value pairs
#	key = human friendly name eg: Karen's House
#	value = correct address in format Street, City, State Zip Code
#	evaluation locations are the constants that you want to check
#	each central location against

evaluation_points_file = "locations.json"

# Central locations
#	name of file containing json list of key value pairs
#	key = human friendly name eg: 123 Main Apartments
#	value = correct address in format Street, City, State Zip Code
#	central locations are the locations you are testing against
#	each evaluation point

central_points_file = "central.json"

################


with open(evaluation_points_file) as locations:
	evaluation_points = json.load(locations)

with open(central_points_file) as central:
	central_points = json.load(central)


url = "https://maps.googleapis.com/maps/api/distancematrix/json?"
result_string = "Distance from {} to {} = {} ~ {}"

statistics = {}

# iterate over the central locations
for central_label, central_address in central_points.items():
	query = {
		'origins': central_address,
		'units': 'imperial'
	}
	
	ten_miles = []
	thirty_minutes = []

	print("Now analyzing {} ({})".format(central_label, central_address)) 

	# for each central location, check the evaluation locations
	for label,address in evaluation_points.items():
		query['destinations'] = address # Add to query dictionary
		params = urllib.parse.urlencode(query)

		f = urllib.request.urlopen(url + params)
		results = json.loads(f.read().decode('utf-8'))["rows"][0]["elements"][0]

		try:
			if float(results["distance"]["text"].split()[0]) < 10 or results["distance"]["text"].split()[1] == "ft":
				ten_miles.append("{} ({})".format(label, results["distance"]["text"]))

			if float(results["duration"]["text"].split()[0]) < 30 and results["duration"]["text"].split()[1] in ["min", "mins"]:
				thirty_minutes.append("{} ({})".format(label, results["duration"]["text"]))

			if verbose:
				print(result_string.format(central_label, label, results["distance"]["text"], results["duration"]["text"]))

		except KeyError:
			print("Error with either the central address or evaluation address.")
			exit(1)
			# Please note, I do not do extensive error checking. 
			# This may be the error of the central address OR the evaluation address
			# Please use your best judgement to debug

	if summary:
		print("Final Results:")
		print("{} is less than 10 miles from {} places:\n\t{}".format(central_label, str(len(ten_miles)), ",\n\t".join(ten_miles)))
		print("{} is less than 30 minutes from {} places:\n\t{}".format(central_label, str(len(thirty_minutes)), ",\n\t".join(thirty_minutes)))


	statistics[central_label] = [(len(ten_miles) / len(evaluation_points.items())) * 100, (len(thirty_minutes) / len(evaluation_points.items())) * 100]

for label, stats in statistics.items():
	print("{} is within 10 miles of {}% and within 30 mins of {}% of locations given".format(label, round(stats[0], 0), round(stats[1], 0)))
