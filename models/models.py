from google.appengine.ext import ndb
from google.appengine.api import memcache

import datetime, time

class User(ndb.Model):
	name = ndb.StringProperty(required = True)
	pw_hash = ndb.StringProperty(required = True)
	created = ndb.DateTimeProperty(auto_now_add = True)
	
	expenses = ndb.KeyProperty(kind='Expense', repeated=True)

	def getAllExpenses(self):
		# This function uses memcache to save on database queries
		expenses = memcache.get(self.name+'expenses')
		if expenses:
			print "Found Records in Memcache"
			return expenses
		else:
			print "No Records in Memcache, retreiving from NDB"
			expenses = Expense.query(Expense.userKey==self.key).order(-Expense.created).fetch()
			memcache.add(self.name+'expenses', expenses)
			return expenses

	def clearCache(self):
		memcache.delete(self.name+'expenses')

	def getExpensesByTags(self, tags):
		expenses = self.getAllExpenses()
		passedExpenses = []
		for expense in expenses:
			if set(tags).issubset(set(expense.tags)):
				passedExpenses.append(expense)
		return passedExpenses

	def getCurrentMonthTotal(self):
		tags = datetime.datetime.now().strftime("%Y,%B").split(",")
		return self.getTotalByTags(tags)

	def getTotalByTags(self, tags):
		expenses = self.getExpensesByTags(tags)
		return Expense.sumExpenses(expenses)

	def getTotal(self):
		return Expense.sumExpenses(self.getAllExpenses())

#-----------------------------------------------------------------------------------

class Expense(ndb.Model):
	amount 	 = ndb.IntegerProperty(required = True)
	category = ndb.StringProperty(required = True, default="General")
	description = ndb.StringProperty(default="")
	userKey = ndb.KeyProperty(kind='User')
	tags = ndb.StringProperty(repeated=True)
	created = ndb.DateTimeProperty(auto_now_add = True)

	@staticmethod
	def sumExpenses(expenses):
		return sum([expense.amount for expense in expenses])
#-----------------------------------------------------------------------------------

class Tag(ndb.Model):
	userKey = ndb.KeyProperty(kind='User')
	name = ndb.StringProperty(required=True)
	expenses = ndb.KeyProperty(kind='Expense', repeated=True)	

	@classmethod
	def addToTag(cls, tag, expense):
		t = Tag.query(ndb.AND(Tag.name==tag, Tag.userKey==expense.userKey)).get()
		if not t:
			t = Tag(userKey=expense.userKey, name=tag)
		t.expenses.append(expense.key)
		t.put()
#-----------------------------------------------------------------------------------	