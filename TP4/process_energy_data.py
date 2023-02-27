import json
import matplotlib.pyplot as plt
import numpy as np
import sys
import copy
from time import strptime, mktime
import re # regexp
from datetime import datetime, timezone


DELTA_UTC = -1*3600
WATT_S = 1/3600 # expressed in WATT_H
INTERVAL_BOUNDARY = 10 # to plot only the experiments

def read_computation_time_aux(data,pause):
	# Time has been obtained with a unix "date", UTC+0
	# Read starting time 
	date=mktime(strptime(data[0][0:-1])) # remove \n
	#print(date)
	comp_times = []
	cumulated_time = 0
	ind = 0
	# Read computation time
	for m in re.finditer(',',data[1]):
		comp_times.append(float(data[1][ind:m.start()]))
		cumulated_time+=comp_times[-1]+pause
		ind = m.end()
	# Read N values
	N_values = []
	ind = 0
	for m in re.finditer(',', data[2]):
		N_values.append(int(data[2][ind:m.start()]))
		ind = m.end()
		
	#print(date+cumulated_time)
	#print(mktime(strptime(data[3][0:-1])) )
	return date, comp_times, N_values


def read_computation_time_file(filename,pause=20):
	# Return temporal instants where to compute energy
	# BE CAREFULL, take into account pause time
	# - filename: .txt file with a specific format to store computation times
	
	with open(filename) as file:
		data = file.readlines()
		#for l in data:
		#	print("new Line:" + l)
		n = len(data)
		all_dates = []
		all_comp_times = []
		all_N = []
		n_languages = (n+1) // 3
		print(data)
		
		for i in range(n_languages):
			date, comp_times, N_values = read_computation_time_aux(data[3*i:3*(i+1)+1],pause)
			print(date)
			all_dates.append(date)
			all_comp_times.append(comp_times)
			all_N.append(N_values)
		#print(date)
		#print(comp_times)
		#date, comp_times = read_computation_time_aux(data[3:],pause)
		#print(date)
		#print(comp_times)
		return all_dates,all_comp_times, all_N
	
def extract_point_timestamp(data_dict,i):
	# there may be timestamps  with non round seconds
	string_i = data_dict[i]['timestamp']
	ind_point = string_i.find(".")
	ind_plus = string_i.find("+")

	if ind_point != -1:
		data_dict[i]['timestamp']= string_i[0:ind_point]+string_i[ind_plus:]

def read_json(filename,shift):
	# shift: translation in seconds to be applied to json times, UTC+2 or UTC+1
	with open(filename) as json_data:
		data_dict = json.load(json_data)

	n = len(data_dict)
	power = np.zeros(n)
	timestamp = []

	for i in range(n):
		power[i] = data_dict[i]['value']
		extract_point_timestamp(data_dict,i)
		t = datetime.timestamp(datetime.fromisoformat( data_dict[i]['timestamp'] ) ) + shift
		timestamp.append(t)
		# print(t)
	#d0 = datetime.timestamp(datetime.fromisoformat(data_dict[0]['timestamp']))
	#print(d0+shift)
	#print(datetime.fromtimestamp(d0, tz=timezone.utc)) # correct solution, but a bit complicated
	return power,timestamp
		
		
def argmin(t_samples,t_0):
	# find index ind such as t_sample[ind]-t_0 is the lowest in absolute value
	ind = 0
	t_min = abs(t_samples[ind]-t_0)
	for i,t in enumerate(t_samples):
		if abs(t-t_0)<t_min:
			t_min = abs(t-t_0)
			ind = i
	return ind
	

def get_good_indices(timestamp,date_0,comp_times,pause=20):
	# date_0, comp_times: for each language, reference and computation times 
	# timestamp: regular temporal instants where to extract indices corresponding to the previous line
	t0 = date_0
	indices = []
	for ct in comp_times: # pas ce qu'il y a de plus optimal mais bon...
		i0 = argmin(timestamp,t0)
		i1 = argmin(timestamp,t0+ct) 
		indices.append([i0,i1])
		t0+=ct+pause
	return indices


def plot_power(power, all_dates=None, all_comp_times=None,timestamp=None):
	# Plot Power and specific temporal intervals
	plt.figure()
	plt.plot(power)
	plt.xlabel('Seconds')
	plt.ylabel('Power (Watts)')
	plt.ylim([0,max(power)])
	
	if all_dates == None:
		plt.show()
		return
	start_time = 0
	end_time = 0
	for date_0, comp_times in zip(all_dates,all_comp_times):
		indices = get_good_indices(timestamp,date_0,comp_times)
		if start_time == 0: # get the first index 
			start_time = indices[0][0]
		end_time = indices[-1][1]
		for extremities in indices:
			plt.fill_between(range(extremities[0],extremities[1]),power[extremities[0]:extremities[1]],alpha=0.5)
	
	plt.xlim([start_time -INTERVAL_BOUNDARY,end_time + INTERVAL_BOUNDARY])
	plt.show()

def integrate(power,ind0,ind1,step):
	integral = 0
	for i in range(ind0,ind1+1):
		integral+=power[i]*step
	return integral


def compute_energy(power,  all_dates=None, all_comp_times=None,timestamp=None):
	all_energies=[]
	# Integration, rectangle method
	for date_0, comp_times in zip(all_dates,all_comp_times):
		indices = get_good_indices(timestamp,date_0,comp_times)
		energies = []
		for extremities in indices:
			energies.append(integrate(power,extremities[0],extremities[1],timestamp[1]-timestamp[0])*WATT_S)
		all_energies.append(energies)
	return all_energies
	


if __name__=="__main__":
	# Extract data
	if len(sys.argv)<2:
		sys.exit("You need to indicate the json filename")
	
	if len(sys.argv)==3:
		all_dates,all_comp_times, all_N = read_computation_time_file(sys.argv[2])
		print(all_dates)
		print(all_comp_times)
		
	power,timestamp = read_json(sys.argv[1],DELTA_UTC)
	print(timestamp)
	# Plot power
	if len(sys.argv)==3:
		plot_power(power, all_dates, all_comp_times,timestamp)
	else:
		plot_power(power)
		exit()
		
	# Plot power w.r.t N
	all_energies = compute_energy(power,  all_dates, all_comp_times,timestamp)
	print(all_energies)
	print(all_N)
	