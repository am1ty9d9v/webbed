# coding: utf8
from django.utils.safestring import SafeUnicode
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django import forms
from bs4 import BeautifulSoup
import urllib
import urllib2
import MySQLdb
import datetime
import re, io
from django.views.decorators.http import condition
from urlparse import urlparse

class search_form(forms.Form):
	link = forms.CharField()
	
def search(request):
	return render_to_response('search.html',{})

def make_function_dict(page):
	# Open the documentation HTML file and read it into BeautifulSoup.
	f = io.open(page)
	s = f.read()
	f.close()
	soup = BeautifulSoup(s)

	# Create an empty dict that will map function names to HTML.
	function_dict = {}

	# Find all 'dl' tags with the css class 'function'
	functions = soup.find_all('dl', {'class':'function'})
	for i in range(0, len(functions)):
		title_tag = functions[i].find('tt', {'class':'descname'})
		name = title_tag.text
		
		desc_tag = functions[i].find('dd')
		desc = desc_tag.text
		function_dict[name] = desc

	return function_dict
    
@condition(etag_func=None)			
def search_results(request):
	try:
		keyword = request.GET.get('keyword', '').strip().lower()
	
		db = MySQLdb.connect("localhost","root","Meethimtat9314","webbed", charset='utf8')
		cursor = db.cursor()
		#remove the below comments when you need to insert into db
		#dict = {}
		#dict = make_function_dict('/home/amit/Desktop/django/webbed/static/python-docs/library/functions.html')
		#for i in dict.items():	
			#sql = """INSERT INTO python_docs (term, definition) VALUES (%s, %s)"""
			#cursor.execute(sql, (i[0], i[1]))
		sql = cursor.execute("SELECT * FROM python_docs")
		rows = cursor.fetchall()
		help_html = "Not found!"
		
		
		for row in rows:
			if row[1] == keyword:
				help_html = row[2]
		#if help_html == None:
			#help_html = "Not found!"
		db.commit()
		db.close()
	except:
		return render_to_response('error.html')
		
	return render_to_response('search_results.html',{'keyword': keyword, 'help_html': help_html, 'rows': rows})




@condition(etag_func=None)		
def extract_links(request):
	try:
		if (request.method == 'GET'):
			form = search_form(request.GET)
			if (form.is_valid()):
				link = form.cleaned_data['link']
				new_link = urlparse(link)
				if new_link.scheme:
					link = new_link.netloc
					link = "http://" + link
				else:
					link = "http://" + link
				starting_link = urllib.urlopen(link)
				soup = BeautifulSoup(starting_link)
				all_links = soup.findAll('a', href = True)	
				all_links = [i.attrs['href'] for i in all_links]	
				var_string  = '\n '.join(all_links)
		
				usock = urllib2.urlopen(link)
				html_source = usock.read()
				usock.close()
				soup = BeautifulSoup(html_source)
				title = soup.title.string

				db = MySQLdb.connect("localhost","root","Meethimtat9314","webbed" )
				cursor = db.cursor()
				sql = """INSERT INTO links_link (all_links, website_name, html_source, title_of_url) VALUES (%s, %s, %s, %s)"""
				cursor.execute(sql,(var_string, link, html_source, title))
				db.commit()
				db.close()
		else:
			return render_to_response('search.html',{})
		
		return render_to_response('extracted_links.html',{'all_links': all_links, 'link': link })
	except:
		return render_to_response('error.html')
	
