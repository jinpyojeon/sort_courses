from bs4 import BeautifulSoup
import re
import requests
import json
import os

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
