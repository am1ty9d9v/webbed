
def test():
	dict = {}
	import final_crawler
	dict = final_crawler.start_crawl()
	for i in dict.items():
		print i[0]
		
if __name__ == "__main__":
	test()
