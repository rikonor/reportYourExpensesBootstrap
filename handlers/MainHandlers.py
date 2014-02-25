import os, sys

from BaseHandler import BaseHandler
from models.models import *

from google.appengine.api.images import get_serving_url

#--------------------------------------------------------------
# MainPage handler
#--------------------------------------------------------------
class MainPage(BaseHandler):

    def get(self):

        self.redirect("/new")
#--------------------------------------------------------------
class AddPageHandler(BaseHandler):

    def get(self):

        self.render("new.html",
        	totalAmount = Expense.getTotal(),
        )

    def post(self):
    	e = Expense()

        if (self.request.get("amount").isdigit()):
            e.amount = int(self.request.get("amount"))
            e.category = self.request.get("category")
            e.description = self.request.get("description")
            e.put()
            time.sleep(0.1)

        return self.response.write(Expense.getTotal())

#--------------------------------------------------------------
class HistoryPageHandler(BaseHandler):

    def get(self):

        self.render("history.html",
        	allExpenses = Expense.getAll(),
        )
#--------------------------------------------------------------