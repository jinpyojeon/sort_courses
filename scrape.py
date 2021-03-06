from bs4 import BeautifulSoup
import re
import requests
import json
import os
import string
from pymongo import MongoClient, DESCENDING, ASCENDING

save_directory = 'courses/' 
main_url = 'http://internet2.trincoll.edu'
search_url = 'http://internet2.trincoll.edu/ptools/CourseSearch.aspx'

def get_course_terms():
	r = requests.get(search_url)
	soup = BeautifulSoup(r.content, 'html.parser')
	terms = soup.find('select', {'id': 'ddlTerm' })
	
	terms_dict = {}
	for t in terms.find_all('option'):
		term_id = t.get('value')
		term_name =  t.getText()
		terms_dict[term_name] = term_id
	
	return terms_dict

def save_courses():
	if not os.path.isdir(save_directory):
		os.makedirs(save_directory) 

	f = open('view.json', 'r')

	json_obj = json.load(f)

	terms_dict = get_course_terms()
	
	latest_term_id = max(terms_dict.items(), key=lambda k : k[1])[1]

	print latest_term_id 
	return

	req_data = dict(ddlTerm=str(latest_term_id), 
			ddlLevel=0,
			ddlCourseCareer='URGD', 
			daysGroup='optInclude',
			ddlSession='REG', 
			butSubmit='Search',
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
	
	print 'Downloading {0} course information'.format(len(course_urls))
	for i, l in enumerate(course_urls):
		course_url = main_url + l
		file_loc = save_directory + l[-4:] + '.html'
		print '\r {0} course from {1} and saving to {2}'.format(
			i, course_url, file_loc), 
		course_info = requests.get(course_url, allow_redirects=True).content
		course_file = open(file_loc, 'w+')
		course_file.write(course_info)
		course_file.close()

def parse_files():
	if not os.path.isdir(save_directory):
		save_courses()

	client = MongoClient()
	db = client['test']
	course_coll = db['courses']

	for f in os.listdir(save_directory):
		course_file = open(save_directory + f, 'r')
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
	#get_course_terms()
	save_courses()
	# parse_files()


