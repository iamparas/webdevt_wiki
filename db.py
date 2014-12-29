from google.appengine.ext import db
import hashlib
import random
from string import letters
#USER ACCOUNT DATABASE/ handles userinfo,login,logouts
def gen_rand():
    length=5
    return ''.join(random.choice(letters) for x in xrange(length))
def gen_hash_pw(name,pw,salt=None):
    if not salt:
        salt=gen_rand()
    hashp=hashlib.sha256(name+pw+salt).hexdigest()
    return '%s,%s'%(salt,hashp)
def users_key(group='default'):
    return db.Key.from_path('users',group)
def valid_pw(name,password,h):
    salt=h.split(',')[0]
    return h==gen_hash_pw(name,password,salt)
class user_acc(db.Model):               
    username=db.StringProperty(required=True)
    password=db.StringProperty(required=True)
    email=db.StringProperty(required=True)
    submitted=db.DateTimeProperty(auto_now_add=True)
    
    @classmethod
    def by_id(cls,uid):
        return user_acc.get_by_id(uid,parent=None)
    @classmethod
    def by_name(cls,name):
        #u=db.GqlQuery("SELECT * FROM user_acc WHERE username='"+name+"'")
        u=user_acc.all().filter('username =',name).get()
        return u
    @classmethod
    def register(cls,username,password,email):
        password_protected=gen_hash_pw(username,password)
        return user_acc(username=username,password=password_protected,email=email)
    @classmethod
    def login(cls,name,pw):
        user=cls.by_name(name)
        if user and valid_pw(name,pw,user.password):
            return user
class user_book(db.Model):
    username=db.StringProperty()
    booktitle=db.StringProperty(required=True)
    isbn=db.StringProperty()
    author=db.StringProperty(required=True)
    desc=db.TextProperty()
    date_req_start=db.DateTimeProperty()
    date_req_end=db.DateTimeProperty()
    comments=db.TextProperty()
    date_submitted=db.DateTimeProperty(auto_now_add=True)
    iswish=db.BooleanProperty()

    @classmethod
    def get_all(cls,name):
        return db.GqlQuery("SELECT * FROM user_book WHERE username='"+name+"'")
    @classmethod
    def get_by_query(cls,query):
        return db.GqlQuery("SELECT * FROM user_book WHERE booktitle='"+query+"'")
    @classmethod
    def check_by_name(cls,bookname,iswish):
        return db.GqlQuery("SELECT * FROM user_book WHERE booktitle='"+bookname+"'")
    
    
class user_match(db.Model):
    user_wish=db.StringProperty()
    user_have=db.StringProperty()
    booktitle=db.StringProperty()
    comments=db.TextProperty()

    @classmethod
    def get_all(cls,name):
        hmatch=db.GqlQuery("SELECT * FROM user_match WHERE user_have='"+name+"'")
        return hmatch
            
