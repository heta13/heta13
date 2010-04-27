import cgi
import os
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.runtime import DeadlineExceededError

class TestPage(webapp.RequestHandler):
  def get(self):
    user = users.get_current_user()

    if user:
      acctinfo = ("%s | <a href=\"%s\">sign out</a>" %
                  (user.email(), users.create_logout_url(self.request.uri)))
      headerline = ('<html><body><p align=right>%s'
                    '</p><hr></body></html>' % acctinfo)
      self.response.out.write(headerline)
    else:
      self.redirect(users.create_login_url(self.request.uri))
    
class Greeting(db.Model):
  author = db.UserProperty()
  content = db.StringProperty(multiline=True)
  date = db.DateTimeProperty(auto_now_add=True)


class MainPage(webapp.RequestHandler):
  def get(self):
    try:
      greetings_query = Greeting.all().order('-date')
      greetings = greetings_query.fetch(10)

      if users.get_current_user():
        url = users.create_logout_url(self.request.uri)
        url_linktext = 'Logout'
      else:
        url = users.create_login_url(self.request.uri)
        url_linktext = 'Login'

      template_values = {
        'greetings': greetings,
        'url': url,
        'url_linktext': url_linktext,
        }

      path = os.path.join(os.path.dirname(__file__), 'index.html')
      self.response.out.write(template.render(path, template_values))
    except DeadlineExceededError: #when request are more than 30 sec. time out.
      self.response.clear()
      self.response.set_status(500)
      self.response.out.write("This operation could not be completed in time...")  

class Guestbook(webapp.RequestHandler):
  def post(self):
    greeting = Greeting()

    if users.get_current_user():
      greeting.author = users.get_current_user()

    greeting.content = self.request.get('content')
    greeting.put()
    self.redirect('/')


application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                      ('/sign', Guestbook),
                                      ('/test', TestPage)],
                                     debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
