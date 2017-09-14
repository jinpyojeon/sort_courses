from bs4 import BeautifulSoup
import re
import requests
import json
import os
import string
from pymongo import MongoClient, DESCENDING, ASCENDING

def save_courses():
	f = open('view.json','r')

	json_obj = json.load(f)

	main_url = 'http://internet2.trincoll.edu'
	search_url = 'http://internet2.trincoll.edu/ptools/CourseSearch.aspx'

	req_data = dict(ddlTerm='1181', ddlLevel=0,
					ddlCourseCareer='URGD', daysGroup='optInclude',
					ddlSession='REG', butSubmit='Search',
					__VIEWSTATE=json_obj['__VIEWSTATE'], 
					__VIEWSTATEGENERATOR=json_obj['__VIEWSTATEGENERATOR'])

	r = requests.post(search_url, data=req_data, allow_redirects=True)

	soup = BeautifulSoup(r.content, 'html.parser')

	print soup.title

	course_urls = []
	for link in soup.find_all('a'):
		l = link.get('href')
		if not l.startswith('/ptools'):
			continue
		course_urls.append(l)

	for l in course_urls:
		print (main_url + l)
		course_info = requests.get(main_url + l, allow_redirects=True).content
		file_loc = '/home/courses/' + l[-4:] + '.html'
		print file_loc
		course_file = open(file_loc, 'w+')
		course_file.write(course_info)
		course_file.close()

def parse_files():
	client = MongoClient()
	db = client['test']
	course_coll = db['courses']

	for f in os.listdir('/home/courses'):
		course_file = open('/home/courses/' + f, 'r')
		soup = BeautifulSoup(course_file.read(), 'html.parser')
		table_entries =  [x.contents for x in soup.find_all('td')]
		proper_string = lambda x : True if x != '\n' and x != ' ' and isinstance(x, basestring) else False
		# print [x[-1] for x in table_entries if proper_string(x[-1])]

		table_entries = [x[-1] for x in table_entries if proper_string(x[-1])]
		
		for i, v in enumerate(table_entries):
			print i, v

		grep_num = lambda x : float(str(x[0]).strip(string.ascii_letters))
		containComma = lambda x : x.find(',') != -1

		class_number = table_entries[0]
		class_name = table_entries[1]
		department = table_entries[2]
		grade_type = table_entries[3]
		class_type = table_entries[4]
		regular_class = True if str(table_entries[5]).decode('utf-8') == 'Regular' else False
		class_credit = table_entries[8]
		class_size_limit = table_entries[9]
		current_class_size = table_entries[10]
		start_date = table_entries[12]
		end_date = table_entries[13]
		class_time = table_entries[14].split(',')[0] if containComma(table_entries[14]) else 'TBA'
		class_location = table_entries[14].split(',')[1] if containComma(table_entries[14]) else 'TBA'
		professor_name = table_entries[15]
		class_requirement = table_entries[16]
		requirement_fulfillment = table_entries[17]
		additional_info = table_entries[18]
		class_description = table_entries[19]

		course = { 
			'class_name': class_name,
			'department': department,
			'grade_type': grade_type,
			'class_type': class_type,
			'is_regular_class': regular_class,
			'class_credit': class_credit,
			'class_size_limit': class_size_limit,
			'current_class_size': current_class_size,
			'start_date': start_date,
			'end_data': end_date,
			'class_time': class_time,
			'class_location': class_location,
			'professor_name': professor_name,
			'class_requirement': class_requirement,
			'requirement_fulfillment': requirement_fulfillment,
			'additional_info': additional_info,
			'class_description': class_description
		}

		course_coll.insert_one(course)

		course_file.close()



if '__main__' == __name__:
	parse_files()


