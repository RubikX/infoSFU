# Author: Edison Suen
# Description: infoSFU aggregates useful information from SFU about courses

import requests
import time

headers = {'User-agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36"}
delimiter = "=============================================================================="

def main():
	print("Welcome to infoSFU")
	ans = True
	while ans:
		print("1. Find general course information\n2. Find information about a section\n3. Exit program")
		ans = input("Please select an option: ")
		if ans == "1":
			course_information()
			print("Would you like to continue? (y/n)")
			user_input = input("").lower()
			if user_input == "y":
				ans = True
			elif user_input == "n":
				ans = False
			else:
				print("Not a valid option")
		elif ans == "2":
			section_information()
			print("Would you like to continue? (y/n)")
			user_input = input("").lower()
			if user_input == "y":
				ans = True
			elif user_input == "n":
				ans = False
			else:
				print("Not a valid option")
		elif ans == "3":
			ans = False
		else:
			print("\nInvalid choice.")


def course_information(): 		
	print("Format: Semester Year Department Course-number",end="\n")
	user_input = input("").split()
	user_input = [i.lower() for i in user_input]

	if user_input[0].lower() == 'fall':
		final_digit = '7'
	elif user_input[0].lower() == 'spring':
		final_digit = '1'
	else: # summer
		final_digit = '4'

	term_code = int('1'+user_input[1][-2:]+final_digit)

	calender_url = "http://www.sfu.ca/bin/wcm/academic-calendar?{}/{}/courses/{}/{}".format(user_input[1],user_input[0],user_input[2],user_input[3])
	sections_url = "http://api.lib.sfu.ca/courses/sections?term={}&department={}&number={}".format(term_code,user_input[2],user_input[3])
	check_sections_url = "http://www.sfu.ca/bin/wcm/course-outlines?{}/{}/{}/{}/".format(user_input[1],user_input[0],user_input[2],user_input[3])
	cycle = ['title','description','prerequisites']

	response = requests.get(calender_url,headers=headers)
	if response.status_code != 200:
		print("Error: ",response.status_code)
	data = response.json()
	print("\n")
	print(delimiter)
	for i in cycle:
		if data[i].find('Prerequisite:') > -1 and data[i] != data['prerequisites']:
			data[i] = data[i][0:data[i].find('Prerequisite:')]
			print(data[i])
		else:
			print(data[i])
		print("\n")
	response_sections = requests.get(sections_url,headers=headers)
	if response.status_code != 200:
		print("Error: ",response.status_code)
	sections = response_sections.json()

	lectures = []
	tutorials = []
	labs = []
	response_check_sections = requests.get(check_sections_url,headers=headers)
	if response.status_code != 200:
		print("Error: ",response.status_code)
	check_sections = response_check_sections.json()
	for i in sections:
		for j in check_sections:
			if i == j['text']:
				if j['sectionCode'] == 'LEC':
					lectures.append(j['text'])
				elif j['sectionCode'] == 'TUT':
					tutorials.append(j['text'])
				else:
					labs.append(j['text'])

	if len(lectures) > 0:
		print("Lecture section(s):",end=" ")
		print(", ".join([x for x in lectures]))

	if len(tutorials) > 0:
		print("Tutorial section(s):",end=" ")
		print(", ".join([x for x in tutorials]))
	if len(labs) > 0:
		print("Lecture section(s):",end=" ")
		print(", ".join([x for x in labs]))
	print(delimiter)
	print("\n")

def section_information():
	print("Format: Semester Year Department Course-number Section")
	user_input = input("").split()
	user_input = [i.lower() for i in user_input]	
	sec_info_url = 'http://www.sfu.ca/bin/wcm/course-outlines?{}/{}/{}/{}/{}'.format(
					user_input[1],user_input[0],user_input[2],user_input[3],user_input[4])
	response = requests.get(sec_info_url,headers=headers)
	if response.status_code != 200:
		print("Error: ",response.status_code)
	sec_info = response.json()
	print("\n")
	print("Instructor: {}".format(sec_info['instructor'][0]['name']))
	print("Start date: {}".format(sec_info['courseSchedule'][0]['startDate'].replace("00:00:00 PDT","").replace("  "," ")))
	print("End date: {}".format(sec_info['courseSchedule'][0]['endDate'].replace("00:00:00 PST","").replace("  "," ")))
	print("Units: {}".format(sec_info['info']['units']))
	print("\n")
	for i in range(len(sec_info['courseSchedule'])):
		print("Day(s): {}".format(sec_info['courseSchedule'][i]['days']))
		print("Location: {} {}, {} campus".format(
									sec_info['courseSchedule'][i]['buildingCode'], 
									sec_info['courseSchedule'][i]['roomNumber'],
									sec_info['courseSchedule'][i]['campus'])
									)
		start_time = time.strptime(sec_info['courseSchedule'][i]['startTime'],"%H:%M")
		start_time = time.strftime( "%-I:%M %p", start_time)
		end_time = time.strptime(sec_info['courseSchedule'][i]['endTime'],"%H:%M")
		end_time = time.strftime( "%-I:%M %p", end_time)
		print("Time: {}-{}".format(start_time, end_time))
		print("\n")
		
	if len(sec_info['examSchedule']) > 0:
		print(delimiter)
		print("Final exam date: {}".format(sec_info['examSchedule'][0]['startDate'].replace("00:00:00 PST","").replace("  "," ")))
		try:
			print("Final exam location: {} {}, {}".format(
										sec_info['examSchedule'][0]['buildingCode'],
										sec_info['examSchedule'][0]['roomNumber'],
										sec_info['examSchedule'][0]['campus'])
										)
		except KeyError:
			print("No location has been currently listed.")
		finalExam_start_time = time.strptime(sec_info['examSchedule'][0]['startTime'],"%H:%M")
		finalExam_start_time = time.strftime( "%-I:%M %p",finalExam_start_time)
		finalExam_end_time = time.strptime(sec_info['examSchedule'][0]['endTime'],"%H:%M")
		finalExam_end_time = time.strftime( "%-I:%M %p",finalExam_end_time)
		print("Final exam time: {}-{}".format(finalExam_start_time, finalExam_end_time))
		print("\n")
	else:
		print("There is no final exam currently listed.")
# ================================================================================

if __name__ == "__main__":
	main()