import cherrypy
import tweepy
import urllib
import uuid
import pymongo


#twitter Auth params
consumer_key="n8fLVWCvVf1TmVM1s44EQ"
consumer_secret="R5ali9P9nNMfJhfny0xvYubfEx6mifp8rX4z5Kk5o"
callback_url = "http://localhost:9031/completeauth"

def maketokens(qty):
	chain = []
	for x in range(0, qty):
		chain.append(str(uuid.uuid4()))
	return chain
	
class start(object):
	def index(self, var=None, **params):
		return "NSTweet"	
	def startauth(self, var=None, **params):
		auth = tweepy.OAuthHandler(consumer_key, consumer_secret, callback_url)
		redirect_url = auth.get_authorization_url()
		cherrypy.session['request_token'] = [auth.request_token.key, auth.request_token.secret]
		cherrypy.response.headers['Location'] = redirect_url
		cherrypy.response.status = 302
	def completeauth(self, var=None, **params):
		oauth_token = urllib.unquote(cherrypy.request.params['oauth_token'])
		oauth_verifier = urllib.unquote(cherrypy.request.params['oauth_verifier'])
		request_token = cherrypy.session.get('request_token')
		auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
		auth.set_request_token(request_token[0], request_token[1])
		auth.get_access_token(oauth_verifier)
		access_token =  auth.access_token.key
		access_secret =  auth.access_token.secret
		tokens = maketokens(100)
		obj = []
		for token in tokens:
			item = {}
			item["token"] = token
			item["access_token"] = access_token
			item["access_secret"] = access_secret
			obj.append(item)
		conn = pymongo.Connection()
		db = conn.nstweet
		tokens = db.tokens
		tokens.insert(obj)
		return tokens
	def tweet(self, var=None, **params):
		token = urllib.unquote(cherrypy.request.params['token'])
		tweet = urllib.unquote(cherrypy.request.params['tweet'])
		conn = pymongo.Connection()
		db = conn.nstweet
		tokens = db.tokens
		result = tokens.find_one({ 'token' : token })
		access_token =  result['access_token']
		access_secret =  result.['access_secret']
		auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
		auth.set_access_token(access_token, access_secret)
		api = tweepy.API(auth)
		api.update_status(tweet)
		tokens.remove(result)
		return "ok"
	index.exposed = True
	startauth.exposed = True
	completeauth.exposed = True
	tweet.exposed = True

cherrypy.config.update('app.cfg')
app = cherrypy.tree.mount(start(), '/', 'app.cfg')
cherrypy.config.update({'server.socket_host': '0.0.0.0',
                        'server.socket_port': 9031})

if hasattr(cherrypy.engine, "signal_handler"):
    cherrypy.engine.signal_handler.subscribe()
if hasattr(cherrypy.engine, "console_control_handler"):
    cherrypy.engine.console_control_handler.subscribe()
cherrypy.engine.start()
cherrypy.engine.block()