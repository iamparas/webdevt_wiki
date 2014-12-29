#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import jinja2
import os
import hashlib
import hmac
import re
import json
import urllib2
import random
from string import letters
#from google.appengine.ext import db
import db
SECMES="du10A010F0Tny89810lkd4n5"

#joins the path of current direcotry with template
temp_dir=os.path.join(os.path.dirname(__file__),'templates')

#loads the file in jinja environment from temp_dir path
jinja_env=jinja2.Environment(loader = jinja2.FileSystemLoader(temp_dir),autoescape=True)


def render_str(self,template,**params):
    t=jinja_env.get_template(template)
    return t.render(params)
def hash_str(s):            
    return hmac.new(SECMES,s).hexdigest()
def make_secure_val(s):
    return "%s|%s"%(s,hash_str(s))
def check_secure_val(h):
    s=h.split('|')[0]
    if(h==make_secure_val(s)):
        return s

class Handler(webapp2.RequestHandler):
    def write(self,*a,**kw):
        self.response.out.write(*a,**kw)
    def render_str(self, template, **params):
        params['user'] = self.user
        t = jinja_env.get_template(template)
        return t.render(params)
    def render(self,template,**kw):
        self.write(self.render_str(template,**kw))
    def set_secure_cookie(self,name,val):
        cookie_val=str(make_secure_val(val))
        self.response.headers.add_header('Set-Cookie','%s=%s; Path=/'%(name,cookie_val))
    def read_secure_cookie(self,name):
        cookie_val=self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)
    def login(self,user):
        self.set_secure_cookie('user_id',str(user.key().id()))

    def logout(self):
        self.response.headers.add_header('Set-Cookie','user_id=; Path=/')

    def initialize(self,*a,**kw):
        #called by app engine framework for every page
        webapp2.RequestHandler.initialize(self,*a,**kw)
        uid=self.read_secure_cookie('user_id')
        #self.response.out.write(uid)
        self.user=uid and db.user_acc.by_id(int(uid)) #
def gen_rand():
    length=5
    return ''.join(random.choice(letters) for x in xrange(length))
def gen_hash_pw(name,pw,salt=None):
    if not salt:
        salt=gen_rand()
    hashp=hashlib.sha256(name+pw+salt).hexdigest()
    return '%s,%s'%(salt,hashp)
def valid_pw(name,password,h):
    salt=h.split(',')[0]
    return h==gen_hash_pw(name,password,salt)


class MainHandler(Handler):
    def get(self):
        user=""
        if self.user:
           user=self.user.username
        self.render("index.html",userperson=user)
    def post(self):
        self.redirect("/login")
class Login(Handler):
    def get(self):
        user=""
        if self.user:
           user=self.user.username
        self.render("login.html",userperson=user)
    def post(self):
        error="The Username you provided already exist"
        chk=self.request.get('process')
        if chk=="signup":
            username=self.request.get("username")
            password=self.request.get("password")
            repass=self.request.get('repassword')
            email=self.request.get("email")
            if password !=repass:
                self.render('index.html',pass_message="Password do not match")
            else:#
                p=db.user_acc.by_name(username)
                if p:
                    self.render("index.html",message=error)
                else: #
                    p=db.user_acc.register(username=username,password=password,email=email)
                    p.put()
                    self.set_secure_cookie('user_id',str(p.key().id()))
                    self.redirect('/start')
        elif chk=='signin':
            username=self.request.get("uname")
            password=self.request.get("pass")
            u=db.user_acc.login(username,password)#
            if u:
                self.login(u)
                self.redirect('/start')
            else:
                msg="Invalid Login Info"
                self.redirect('/')

class Logout(Handler):#handles user logout 
    def get(self):
        self.logout()
        self.redirect('/')
app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/login',Login),
    ('/logout',Logout),
], debug=True)
