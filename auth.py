
import hmac
import hashlib
from secret import APP_KEY, SECRET_KEY
import simplejson, urllib2

def http_auth(username, password):
    def hmac_sha1(value):
        maker = hmac.new(SECRET_KEY, value, hashlib.sha1)
        return maker.hexdigest()
    def hmac_pass():
        return hmac_sha1(hashlib.md5(password).hexdigest())
    auth_url = 'http://langdev.org/apps/' + APP_KEY + '/sso/' + username
    req = urllib2.Request(auth_url, 'password=' + hmac_pass(), {'Accept': 'application/json'})
    try:
        return simplejson.load(urllib2.urlopen(req))
    except:
        return False

