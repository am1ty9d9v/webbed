import MySQLdb
def crawl_now():
	db = MySQLdb.connect("localhost","root","Meethimtat9314","webbed", charset='utf8')
	
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
		sql = """INSERT INTO url_info (url, title, description) VALUES (%s, %s, %s)"""
		cursor.execute(sql, (url, title, description))
	db.commit()
	db.close()
	return None
	
if __name__ == "__main__":
	crawl_now()
		
