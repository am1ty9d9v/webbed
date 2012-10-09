# coding: utf8


#/*********************************************************************************************

#Project : A web crawler cum search engine
#URI: http://www.webbed.co.cc/
#Version: 1.0
#Author: Amit Yadav
#Author URI: http://www.amityadav.in
#Github URI: https://github.com/am1ty9d9v/webbed

#**********************************************************************************************


from django.utils.safestring import SafeUnicode
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django import forms
from bs4 import BeautifulSoup
import urllib
import operator
import urllib2
import MySQLdb
import datetime, time
import re, io
from django import template
from django.views.decorators.http import condition
from django.template.context import RequestContext
from urlparse import urlparse
from django.utils.safestring import SafeString

class search_form(forms.Form):
	link = forms.CharField()
	
def search(request):
	return render_to_response('search.html',{})
	
def feedback(request):
	return render_to_response('feedback.html',{})


@condition(etag_func=None)	
def search_results(request, autoescape=None):
	#try:
	
	keyword = request.GET.get('keyword', '').strip().lower()
	if keyword == "":
		keyword = "amit yadav"
	splitted_keyword = keyword.split()

	db = MySQLdb.connect("localhost","root","9314","webbed", charset='utf8')
	cursor = db.cursor()
	
	start_time = time.time()
	sql = cursor.execute("SELECT * FROM index_table ")
	rows_of_index_table = cursor.fetchall()
	
	sql1 = cursor.execute("SELECT * FROM url_info ORDER BY pagerank DESC")
	rows_of_url_info = cursor.fetchall()
	#print rows_of_url_info
	end_time = time.time()
	total_time = end_time - start_time
	all_urls = "Not found!"
	
	#count = 0
	for row in rows_of_index_table:
		for each_word in splitted_keyword:
			if row[1] == each_word:
				all_urls = row[2]
		#count += 1
	list_of_all_urls = all_urls.split(', ')
	
	for count, i in enumerate(list_of_all_urls):
		pass
	count = count + 1
	
	stopwords = ['a', 'able', 'about', 'across', 'after', 'all', 'almost', 'also', 'am', 'among', 'an', 'and', 'any', 'are', 'as', 'at', 'be', 'because', 'been', 'but', 'by', 'can', 'cannot', 'could', 'dear','did', 'do', 'does', 'either', 'else', 'ever', 'every', 'for', 'from', 'get', 'got', 'had', 'has', 'have','he', 'her', 'hers', 'him', 'his', 'how', 'however', 'i', 'if', 'in', 'into', 'is', 'it', 'its', 'just','least', 'let', 'like', 'likely', 'may', 'me', 'might', 'most', 'must', 'my', 'neither', 'no', 'nor', 'not','of', 'off', 'often', 'on', 'only', 'or', 'other', 'our', 'own', 'rather', 'said', 'say', 'says', 'she','should', 'since', 'so', 'some', 'than', 'that', 'the', 'their', 'them', 'then', 'there', 'these', 'they','this', 'tis', 'to', 'too', 'twas', 'us', 'wants', 'was', 'we', 'were', 'what', 'when', 'where', 'which','while', 'who', 'whom', 'why', 'will', 'with', 'would', 'yet', 'you', 'your']

	
	url_desc = {}
	for j in rows_of_url_info:
		m = re.findall(keyword, j[3])
		index_list = [n.start() for n in re.finditer(keyword, j[3])]
		#print index_list
		#print m
		desc_list = []
		if m:
			for i in m:
				for k in index_list:
					a = j[3].find(keyword, k)
					#print "a===", a
					z = len(keyword)
					z = z+a
					desc = j[3][a-60:a] + "<b>" + i + "</b> " + j[3][z+1: z+80]
					#print desc
					try:
						desc_list.append(desc)
					except: 
						print "error"
						pass
		else:
			for each_word in splitted_keyword:
				if each_word not in stopwords:
					#j[3] = j[3].lower()
					a = j[3].find(each_word)
					z = len(each_word)
					z = z+a
					m = re.search(each_word, j[3])
					if m:
						desc = j[3][a-60:a] + "<b>" + m.group() + "</b> " + j[3][z+1: z+80]
						try:
							desc_list.append(desc)
						except: 
							print "error"
							pass
		b = "   <b> . . . </b>   ".join(desc_list[0:3])
		b = b + "<b> . . . </b>"
		url_desc[j[1]] = [j[4], b]
	url_desc1 = sorted(url_desc.iteritems(), key=operator.itemgetter(1), reverse = True)
	#print url_desc1
		
			
	
	db.commit()
	db.close()
	#except:
		#return render_to_response('error.html')
		
	return render_to_response('search_results.html',{'keyword': keyword, 'list_of_all_urls': list_of_all_urls, 'rows_of_index_table': rows_of_index_table, 'rows_of_url_info': rows_of_url_info, 'url_desc1': url_desc1, 'all_urls':all_urls, 'count':count, 'total_time':total_time},context_instance=RequestContext(request))

		
@condition(etag_func=None)
def crawl_now(request):
	db = MySQLdb.connect("localhost","root","9314","webbed", charset='utf8')
	cursor = db.cursor()
	#remove the below comments when you need to insert into db
	
	index = {}
	import final_crawler
	index, pagedata = final_crawler.start_crawl()
	#var = dict.keys()
	cursor.execute("TRUNCATE TABLE `index_table`")
	cursor.execute("TRUNCATE TABLE `url_info`")
	import json
	for i in index.items():
		term = i[0]
		urls = ', '.join(i[1])
		sql = """INSERT INTO index_table (term, urls) VALUES (%s, %s)"""
		cursor.execute(sql, (term, urls))
	for i in pagedata.items():
		url = i[0]
		title = i[1][0]
		description = i[1][1]
		pagerank = i[1][2]
		sql = """INSERT INTO url_info (url, title, description, pagerank) VALUES (%s, %s, %s, %s)"""
		cursor.execute(sql, (url, title, description, pagerank))
	db.commit()
	db.close()
	return render_to_response('update_index.html')
	
