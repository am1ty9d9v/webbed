from django.db import models

class Link(models.Model):
	all_links = models.TextField()
	website_name = models.TextField()
	html_source = models.TextField()
	title_of_url = models.TextField()
	def __unicode__(self):
		return u'%s %s %s %s' % (self.all_links, self.website_name, self.html_source, self.title_of_url)


