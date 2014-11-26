from google.appengine.ext import ndb
from google.appengine.api import memcache

import datetime, time

class User(ndb.Model):
	name = ndb.StringProperty(required = True)
	pw_hash = ndb.StringProperty(required = True)
	created = ndb.DateTimeProperty(auto_now_add = True)
	
	tags = ndb.KeyProperty(kind='Tag', repeated=True)

	def getAllTags(self):
		# This function uses memcache to save on database queries
		tags = memcache.get(self.name+'tags')
		if tags:
			print "Found Records in Memcache"
			return tags
		else:
			print "No Records in Memcache, retreiving from NDB"
			tags = Tag.query(Tag.userKey==self.key).order(-Tag.created).fetch()
			memcache.add(self.name+'tags', tags)
			return tags

	def clearCache(self):
		memcache.delete(self.name+'tags')

#-----------------------------------------------------------------------------------

class Tag(ndb.Model):
	# location is a string for "lat,lng"
	location = ndb.StringProperty(default="-13.274961, -163.139033")
	category = ndb.StringProperty(required = True, default="General")
	description = ndb.StringProperty(default="")
	userKey = ndb.KeyProperty(kind='User')
	created = ndb.DateTimeProperty(auto_now_add = True)

	def getDateString(self):
		return self.created.strftime("%d/%m/%Y")

	@staticmethod
	def getCategories():
		return [
			"Store",
            "Competitor",
            "Point of Interest",
		]
#-----------------------------------------------------------------------------------