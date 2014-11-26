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

        # Render Add (Main) Page
        return self.render("new.html",
            categories = Tag.getCategories(),
        )

    def post(self):
        user = Authenticate(self.request)
        if not user:
            return self.redirect("/")

        # Passed - Create expense
        t = Tag(userKey     = user.key,
                location    = self.request.get("location"),
                category    = self.request.get("category"),
                description = self.request.get("description")
        )
        t.put()

        print self.request
        
        user.tags.append(t.key)
        user.put()

        # Clear the cache for this user (so cache refreshes)
        user.clearCache()

        time.sleep(0.1)

        # Set response
        info = {
            'id': t.key.id(),
            'category': t.category,
            'description': t.description,
        }

        self.response.headers['Content-Type'] = 'application/json'
        return self.response.write(json.dumps(info))

#--------------------------------------------------------------
class LocationsPageHandler(BaseHandler):

    def get(self):
        user = Authenticate(self.request)
        if not user:
            return self.redirect("/")

        return self.render("locations.html",
        	allTags = user.getAllTags(),
        )
#--------------------------------------------------------------
class EditPageHandler(BaseHandler):

    def get(self):
        user = Authenticate(self.request)
        if not user:
            return self.redirect("/")

        tag_id = int(self.request.get("id"))
        t = Tag.get_by_id(tag_id)

        if not t:
            return self.redirect("/")

        return self.render("edit.html",
            t = t,
            categories = Tag.getCategories(),
        )

    def post(self):
        user = Authenticate(self.request)
        if not user:
            return self.redirect("/")

        tag_id = int(self.request.get("id"))
        t = Tag.get_by_id(tag_id)
        
        t.category    = self.request.get("category")
        t.description = self.request.get("description")
        t.put()
        
        # Clear the cache for this user (so cache refreshes)
        user.clearCache()

        time.sleep(0.1)

        info = {
            'message': 'success',
            'category': t.category,
            'description': t.description,
        }

        self.response.headers['Content-Type'] = 'application/json'
        return self.response.write(json.dumps(info))
#--------------------------------------------------------------
class RemoveHandler(BaseHandler):

    def post(self):
        user = Authenticate(self.request)
        if not user:
            return self.redirect("/")

        tag_id = int(self.request.get("id"))
        t = Tag.get_by_id(tag_id)
        u = t.userKey.get()
        u.tags.remove(t.key)
        u.put()
        t.key.delete()

        # Clear the cache for this user (so cache refreshes)
        user.clearCache()

        time.sleep(0.1)

        info = {
            'message': 'success',
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