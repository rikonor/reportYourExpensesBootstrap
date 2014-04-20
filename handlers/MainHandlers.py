import os, sys, json, datetime

from BaseHandler import BaseHandler
from AuthHandlers import *
from models.models import *
from security import hashes

from google.appengine.api.images import get_serving_url

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

        year, month = datetime.datetime.now().strftime("%Y,%B").split(",")
        initialTags = [year, month]

        #Get Total for current month
        expenses = Expense.getAllForUser(user)
        passedExpenses = []
        for expense in expenses:
            if set(initialTags).issubset(set(expense.tags)):
                passedExpenses.append(expense)
        currentMonthSum = Expense.sumExpenses(passedExpenses)

        # Render Add (Main) Page
        return self.render("new.html",
            month = month,
            year = year,
        	totalAmount = currentMonthSum,
            initialTags = initialTags,
        )

    def post(self):
        user = Authenticate(self.request)
        if not user:
            return self.redirect("/")

        e = Expense()

        if not self.request.get("amount").isdigit():
            return

        # Passed
        e.userKey     = user.key
        e.amount      = int(self.request.get("amount"))
        e.category    = self.request.get("category")
        e.description = self.request.get("description")
        e.tags        = self.request.get("tagsInput").split(",")
        e.put()

        user.expenses.append(e.key)
        user.put()

        tags = self.request.get("tagsInput").split(",")
        for tag in tags:
            t = Tag.query(ndb.AND(Tag.name==tag, Tag.userKey==user.key)).get()
            if not t:
                t = Tag(userKey=user.key, name=tag)
            t.expenses.append(e.key)
            t.put()

        time.sleep(0.1)

        info = {
            'total': Expense.getTotalForUser(user),
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
            totalSum = Expense.getTotalForUser(user),
        	allExpenses = Expense.getAllForUser(user),
        )
#--------------------------------------------------------------
class JsonExpensesByTags(BaseHandler):

    def get(self):
        user = Authenticate(self.request)
        if not user:
            return self.redirect("/")

        tagNames = self.request.get("tagsInput")

        expenses = Expense.getAllForUser(user)
        passedExpenses = []

        if tagNames:
            tagNames = tagNames.split(",")
            for expense in expenses:
                if set(tagNames).issubset(set(expense.tags)):
                    passedExpenses.append(expense)
        else:
            passedExpenses = expenses

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

        time.sleep(0.1)

        info = {
            'message': 'success',
            'total': Expense.getTotalForUser(user),
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