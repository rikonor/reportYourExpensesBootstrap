import os, sys, json, datetime

from BaseHandler import BaseHandler
from AuthHandlers import *
from models.models import *
from security import hashes

from google.appengine.api.images import get_serving_url

#--------------------------------------------------------------
# Aux functions
#--------------------------------------------------------------
def getCurrentMonthTags():
    year, month = datetime.datetime.now().strftime("%Y,%B").split(",")
    initialTags = [year, month]
    return initialTags
#--------------------------------------------------------------
# MainPage handler
#--------------------------------------------------------------
class MainPage(BaseHandler):

    def get(self):
        user = Authenticate(self.request)
        if not user:
            return self.redirect("/login")

        return self.redirect("/new")
#--------------------------------------------------------------
class AddPageHandler(BaseHandler):

    def get(self):
        user = Authenticate(self.request)
        if not user:
            return self.redirect("/")

        initialTags = getCurrentMonthTags()

        # Render Add (Main) Page
        return self.render("new.html",
            month = initialTags[1],
            year = initialTags[0],
        	totalAmount = user.getCurrentMonthTotal(),
            initialTags = initialTags,
        )

    def post(self):
        user = Authenticate(self.request)
        if not user:
            return self.redirect("/")

        if not self.request.get("amount").isdigit():
            return

        # Passed - Create expense
        e = Expense(userKey     = user.key,
                    amount      = int(self.request.get("amount")),
                    category    = self.request.get("category"),
                    description = self.request.get("description"),
                    tags        = self.request.get("tagsInput").split(","))
        e.put()
        
        user.expenses.append(e.key)
        user.put()

        # Update/Create Tags
        tags = self.request.get("tagsInput").split(",")
        for tag in tags:
            Tag.addToTag(tag, e)

        # Clear the cache for this user (so cache refreshes)
        user.clearCache()

        time.sleep(0.1)

        # Set response
        info = {
            'total': user.getCurrentMonthTotal(),
            'id': e.key.id(),
            'amount': e.amount,
            'category': e.category,
            'description': e.description,
        }

        self.response.headers['Content-Type'] = 'application/json'
        return self.response.write(json.dumps(info))

#--------------------------------------------------------------
class HistoryPageHandler(BaseHandler):

    def get(self):
        user = Authenticate(self.request)
        if not user:
            return self.redirect("/")

        return self.render("history.html",
            totalSum    = user.getTotal(),
        	allExpenses = user.getAllExpenses(),
        )
#--------------------------------------------------------------
class JsonExpensesByTags(BaseHandler):

    def get(self):
        user = Authenticate(self.request)
        if not user:
            return self.redirect("/")

        tagNames = self.request.get("tagsInput")

        if tagNames:
            tagNames = tagNames.split(",")
            passedExpenses = user.getExpensesByTags(tagNames)
        else:
            # Show all (No tags specified)
            passedExpenses = user.getAllExpenses()

        info = []
        for e in passedExpenses:
            info.append({
                'id': e.key.id(),
                'created': e.created.strftime("%D"),
                'amount': e.amount,
                'category': e.category,
                'description': e.description,
                'tags': e.tags,
            })

        self.response.headers['Content-Type'] = 'application/json'
        return self.response.write(json.dumps(info))           
#--------------------------------------------------------------
class EditPageHandler(BaseHandler):

    def get(self):
        user = Authenticate(self.request)
        if not user:
            return self.redirect("/")

        expense_id = int(self.request.get("id"))
        e = Expense.get_by_id(expense_id)

        if not e:
            return self.redirect("/")

        return self.render("edit.html", e = e,)

    def post(self):
        user = Authenticate(self.request)
        if not user:
            return self.redirect("/")

        if not self.request.get("amount").isdigit():
            return

        expense_id = int(self.request.get("id"))
        e = Expense.get_by_id(expense_id)
        
        e.amount      = int(self.request.get("amount"))
        e.category    = self.request.get("category")
        e.description = self.request.get("description")
        e.tags        = self.request.get("tagsInput").split(",")
        e.put()
        
        # Clear the cache for this user (so cache refreshes)
        user.clearCache()

        time.sleep(0.1)

        info = {
            'message': 'success',
            'amount': e.amount,
            'category': e.category,
            'description': e.description,
        }

        self.response.headers['Content-Type'] = 'application/json'
        return self.response.write(json.dumps(info))
#--------------------------------------------------------------
class RemoveHandler(BaseHandler):

    def post(self):
        user = Authenticate(self.request)
        if not user:
            return self.redirect("/")

        expense_id = int(self.request.get("id"))
        e = Expense.get_by_id(expense_id)
        u = e.userKey.get()
        u.expenses.remove(e.key)
        u.put()
        e.key.delete()

        # Clear the cache for this user (so cache refreshes)
        user.clearCache()

        time.sleep(0.1)

        year, month = datetime.datetime.now().strftime("%Y,%B").split(",")
        initialTags = [year, month]

        info = {
            'message': 'success',
            'total': user.getCurrentMonthTotal(),
            'id': self.request.get("id"),
        }

        self.response.headers['Content-Type'] = 'application/json'
        return self.response.write(json.dumps(info))
#--------------------------------------------------------------
class SignupPageHandler(BaseHandler):

    def get(self):
        user = Authenticate(self.request)
        if user:
            return self.redirect("/")

        return self.render("signup.html",
        )

    def post(self):
        user = Authenticate(self.request)
        if user:
            return self.redirect("/")

        # get signup params
        username       = self.request.get("username")
        password       = self.request.get("password")
        passwordrepeat = self.request.get("passwordrepeat")

        # validate
        if not (username and password and password == passwordrepeat):
            return self.redirect("/signup")

        # checK if username is available
        userNamePresent  = User.query(User.name==username).get()
        if userNamePresent:
            return self.redirect("/signup")

        # hash pw
        pw_hash = hashes.make_pw_hash(username, password)
        # create new user
        u = User(name=username,pw_hash=pw_hash)
        u.put()
        # set cookies.
        SetLoginCookies(self, u)
        return self.redirect("/")

#--------------------------------------------------------------
class LoginPageHandler(BaseHandler):

    def get(self):
        user = Authenticate(self.request)
        if user:
            return self.redirect("/")

        return self.render("login.html",
        )

    def post(self):
        user = Authenticate(self.request)
        if user:
            return self.redirect("/")

        # get login params
        username = self.request.get("username")
        password = self.request.get("password")
        userFind = User.query(User.name==username).get()

        # validate
        if not userFind:
            return self.redirect("/")

        if not (username and password):
            return self.redirect("/login")

        # hash pw
        pw_hash = userFind.pw_hash
        if not password or not hashes.valid_pw(username, password, pw_hash):
            return self.redirect("/")

        SetLoginCookies(self, userFind)
        return self.redirect("/new")


#--------------------------------------------------------------
class LogoutPageHandler(BaseHandler):

    def get(self):

        ClearLoginCookies(self)
        return self.redirect("/")
#--------------------------------------------------------------