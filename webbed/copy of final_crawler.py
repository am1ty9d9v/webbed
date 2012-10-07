
# coding=utf8
import urllib, re
import robotexclusionrulesparser as rerp
from bs4 import BeautifulSoup
from urlparse import urlparse, urljoin
import csv

def crawl_web(seed, max_pages, max_depth): # returns index, graph of inlinks
	tocrawl = []
	for url in seed:
		if is_udacity(url):
			tocrawl.append([url, 0])
		else: 
			print "[crawl-web()] This seed is not a amityadav.in site!"
			pass
	crawled = []
	graph = {}  # <url>, [list of pages it links to]
	index = {}
	pagedata = {} 
	while tocrawl: 
		page, depth = tocrawl.pop(0)
		print "[crawl_web()] Depth: ", depth
		print "[crawl_web()] Pages crawled: ", len(crawled)
		if page not in crawled and len(crawled) < max_pages and depth <= max_depth:
			soup, url = get_page(page)
			cache[url] = soup
			get_page_data(soup, url, pagedata)
			print get_page_data(soup, url, pagedata)
			add_page_to_index(index, page, soup)
			
			outlinks = get_all_links(soup, url)
			graph[page] = outlinks
			add_new_links(tocrawl, outlinks, depth)
			#print tocrawl
			crawled.append(page)
			#print crawled
	
	index = undupe_index(index)
	#print "pagedata======= ", pagedata
	return index, graph, pagedata

def visible_texts_from_urls(element):
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
        return False
    
    return True
    
def get_page_data(page, url, dict):
	#url = remove_duplicates(url)
	try:
		title = page.title.string
		if title is None:
			title = url
	except:
		title = url
	try:
		html = urllib.urlopen(url).read()
		soup = BeautifulSoup(html)
		texts = soup.find_all(text=True)
		visible_texts = filter(visible_texts_from_urls, texts)
		text =" ".join(visible_texts) 
		text = " ".join(text.split())
		text = text[:300] 
		text = text + "..."
		#text = str(text)
		#return text
		#text = "szdfzdgxdgfhj"

	except:
		text = 'No description'
	dict[url] = [title, text]
	return dict[url]

def get_all_links(page, url):
	links = []
	page_url = urlparse(url)
	if page_url[0]:
		base = page_url[0] + '://' + page_url[1]
		robots_url = urljoin(base, '/robots.txt')
	else:
		robots_url = "http://blog.amityadav.in/robots.txt"
	rp = rerp.RobotFileParserLookalike()
	rp.set_url(robots_url)
	try:
		rp.read()
	except:
		pass
	#print rp
	for link in page.find_all('a'):
		link_url = link.get('href')
		print "[get_all_links()] Found a link: ", link_url
		#Ignore links that are 'None'.
		if link_url == None: 
			pass
		elif not rp.can_fetch('*', link_url):
			print "[get_all_links] Page off limits!" 
			pass		
		#Ignore links that are internal page anchors. 
		#Urlparse considers internal anchors 'fragment identifiers', at index 5. 
		elif urlparse(link_url)[5] and not urlparse(link_url)[2]: 
			pass
		elif urlparse(link_url)[1]:
			links.append(link_url)
		else:
			newlink = urljoin(base, link_url)
			links.append(newlink)
	return links

def add_new_links(tocrawl, outlinks, depth):
    for link in outlinks:
    	if link:
        	if link not in tocrawl:
        		if is_udacity(link):
        			link = str(link)
        			tocrawl.append([link, depth+1])

def add_page_to_index(index, url, content):
	try:
		text = content.body.get_text()
	except:
		return
	words = text.split()
	punctuation = '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'
	stopwords = ['a', 'able', 'about', 'across', 'after', 'all', 'almost', 'also', 'am', 'among', 'an', 
'and', 'any', 'are', 'as', 'at', 'be', 'because', 'been', 'but', 'by', 'can', 'cannot', 'could', 'dear',
'did', 'do', 'does', 'either', 'else', 'ever', 'every', 'for', 'from', 'get', 'got', 'had', 'has', 'have',
'he', 'her', 'hers', 'him', 'his', 'how', 'however', 'i', 'if', 'in', 'into', 'is', 'it', 'its', 'just',
'least', 'let', 'like', 'likely', 'may', 'me', 'might', 'most', 'must', 'my', 'neither', 'no', 'nor', 'not',
'of', 'off', 'often', 'on', 'only', 'or', 'other', 'our', 'own', 'rather', 'said', 'say', 'says', 'she',
'should', 'since', 'so', 'some', 'than', 'that', 'the', 'their', 'them', 'then', 'there', 'these', 'they',
'this', 'tis', 'to', 'too', 'twas', 'us', 'wants', 'was', 'we', 'were', 'what', 'when', 'where', 'which',
'while', 'who', 'whom', 'why', 'will', 'with', 'would', 'yet', 'you', 'your']
	
	for word in words:
		word = word.lstrip(punctuation)
		word = word.rstrip(punctuation)
		word = word.lower()
		if word not in stopwords:
			add_to_index(index, word, url)
		
        
def add_to_index(index, keyword, url):
    if keyword in index:
        index[keyword].append(url)
    else:
        index[keyword] = [url]

def lookup(index, keyword):
    if keyword in index:
        return index[keyword]
    else:
        return None

def get_page(url):
	page_url = urlparse(url)
	base = page_url[0] + '://' + page_url[1]
	robots_url = base + '/robots.txt'
	rp = rerp.RobotFileParserLookalike()
	rp.set_url(robots_url)
	rp.read()
	if not rp.can_fetch('*', url):
		print "[get_page()] Page off limits!"
		return BeautifulSoup(""), ""
	if url in cache:
		return cache[url], url
	else:
		print "[get_page()] Page not in cache: " + url
		try:
			content = urllib.urlopen(url).read()
			return BeautifulSoup(content), url
		except:
			return BeautifulSoup(""), ""

def compute_ranks(graph):
    d = 0.8 # damping factor
    numloops = 10
    
    ranks = {}
    npages = len(graph)
    for page in graph:
        ranks[page] = 1.0 / npages
    
    for i in range(0, numloops):
        newranks = {}
        for page in graph:
            newrank = (1 - d) / npages
            for node in graph:
                if page in graph[node]:
                    newrank = newrank + d * (ranks[node] / len(graph[node]))
            
            newranks[page] = newrank
        ranks = newranks
    return ranks

def is_udacity(url):
	udacity_urls = ['blog.amityadav.in', 'www.amityadav.in']
	parsed_url = urlparse(url)
	if parsed_url[1] in udacity_urls:
		return True
	
	else:
		return False

def write_search_terms(filename, index):
	f = open(filename, 'wt')
	try:
		writer = csv.writer(f)
		writer.writerow(['term', 'urls'])
		for term in index:
			if len(term) > 500:
				pass
			else:
				ascii_term = term.encode('ascii', 'ignore')
				url_list = index[term]
				urlstring = ",".join(url_list)
				writer.writerow([ascii_term, urlstring])
	finally:
		f.close()
		print "[write_search_terms()] Finished writing SearchTerm CSV file."

def write_url_info(filename, index, ranks, pagedata):
	f = open(filename, 'wt')
	try:
		writer = csv.writer(f)
		writer.writerow(['url', 'title', 'text', 'dave_rank', 'doc'])
		all_urls = set()
		for term in index:
			url_list = index[term]
			for url in url_list:
				
				all_urls.add(url)
		for url in all_urls:
			ascii_url = url.encode('ascii', 'ignore')
			if url in ranks:
				dave_rank = ranks[url]
				doc = False
			else:
				dave_rank = 0.01
				doc = True
			title = pagedata[url][0]
			text = pagedata[url][1]
			ascii_title = title.encode('ascii', 'ignore')
			ascii_text = text.encode('ascii', 'ignore')				
			writer.writerow([ascii_url,ascii_title, ascii_text, dave_rank, doc])
	finally:
		f.close()
		print "[write_url_info()] Finished writing PageUrl CSV file."

def remove_duplicates(seq):
    seen = set()
    seen_add = seen.add
    return [ x for x in seq if x not in seen and not seen_add(x)]
   
    
def rem_trailing_slash(li_urls):
	li = []
	for i in li_urls:
		head, sep, tail = i.partition('index.php')
		j = head.rstrip('/')	
		#j = i.rstrip('/')	
		li.append(j)
	return li
	
def undupe_csv(filename, newfilename):
	oldfile = csv.reader(open(filename, 'rb'))
	newfile = open(newfilename, 'wb')
	try:
		writer = csv.writer(newfile)
		unique_rows = []
		for row in oldfile:
			if row not in unique_rows:
				unique_rows.append(row)
		writer.writerows(unique_rows)
	finally:
		newfile.close()
		print "[undupe_csv()] Index un-duped."

def undupe_index(index):
	for key in index.keys():
		index[key] = list(set(index[key]))
	print "[undupe_index()] Index un-duped"
	return index

			

cache = {}
max_pages = 1000
max_depth = 10
crawl_list = ['http://www.amityadav.in/']
	
def start_crawl():        		
	index, graph, pagedata = crawl_web(crawl_list, max_pages, max_depth)
	new_index = {}
	for i in index.items():
		j = rem_trailing_slash(i[1])
		k = remove_duplicates(j)
		new_index[i[0]] = k
	
		
	ranks = compute_ranks(graph)
	
	#write_search_terms('new_search_terms.csv', new_index)
	#write_url_info('url_info.csv', index, ranks, pagedata)
	#print "INDEX: ", index 
	#write_url_info('url_info.csv', new_index, ranks, pagedata)
	
	return new_index, pagedata
	
	


if __name__ == "__main__":
	start_crawl()


