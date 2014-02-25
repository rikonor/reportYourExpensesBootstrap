from google.appengine.ext import ndb

import datetime, time

class Expense(ndb.Model):
	# Properties
	amount 	 = ndb.IntegerProperty(required = True)
	category = ndb.StringProperty(required = True, default="General")
	description = ndb.StringProperty(default="")
	created = ndb.DateTimeProperty(auto_now_add = True)

	@staticmethod
	def getTotal():
		return sum([expense.amount for expense in Expense.query().fetch()])

	@staticmethod
	def getAll():
		return Expense.query().order(-Expense.created).fetch()