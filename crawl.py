from bs4 import BeautifulSoup
import requests
import requests.exceptions
import urllib.parse
from collections import deque
import re
import mimetypes
from validate_email_address import validate_email

from flask import Flask, jsonify
from flask_restful import Api, Resource
import importlib



def search_url(user_url):
  # user_url = "https://slakenet.com.ng/"
  urls = deque([user_url])

  scraped_urls = set()
  emails = set()

  count = 0
  try:
    while len(urls):
      count += 1
      if count == 200:
        break
      url = urls.popleft()
      scraped_urls.add(url)

      parts = urllib.parse.urlsplit(url)
      base_url = '{0.scheme}://{0.netloc}'.format(parts)

      path = url[:url.rfind('/')+1] if '/' in parts.path else url

      print('[%d] Processing %s' % (count, url))
      # try:
      #   response = requests.get(url)
      # except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError, urllib3.exceptions.LocationParseError):
      #   continue
      strict = True
      link_type, _ = mimetypes.guess_type(url)
      if link_type is None and strict:
        try:
          u = urllib.request.urlopen(url)
          link_type = u.info().get_content_type()
          print(link_type)
          if link_type!="text/html":
            pass
          else:
            try:
              response = requests.get(url)
            except:
              continue
            new_emails = set(re.findall(r'[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+', response.text, re.I))
            emails.update(new_emails)

            soup = BeautifulSoup(response.text, features="lxml")

            for anchor in soup.find_all("a"):
              link = anchor.attrs['href'] if 'href' in anchor.attrs else ''
              if link.startswith('/'):
                link = base_url + link
              elif not link.startswith('http'):
                link = path + link
              if not link in urls and not link in scraped_urls:
                urls.append(link)
        except:
          pass
  except KeyboardInterrupt:
    print('[-] Closing!')

  for mail in emails:
    print(mail)
    # return mail
    return emails

def isValidEmail(email):return validate_email(email)

def organize(url):
    leads = {}
    # emails = ["praisejames011@gmail.com", "hello@slakenet.com.ng", "slakenetofficial@gmail.com"]
    emails = search_url(url)
    for i in emails:
        if isValidEmail(i):
            leads[i] = {"status":"Verified"};
        else:
            leads[i] = {"status":"Invalid"};
    return leads

def scrapeGoogleMap():
    task = "scraper"
    Task = importlib.import_module(task).Task
    t = Task()
    t.begin_task()

app = Flask(__name__)
api = Api(app)

class SearchURL(Resource):
    def get(self, url):
        result = organize(url)
        return jsonify({"success":"true", "leads":result})

class GoogleMap():
    def get(self, queries):
        result = scrapeGoogleMap()
        return jsonify({"success":"true", "leads":result})

api.add_resource(SearchURL, "/search_url/<path:url>")
# Add google map scraping to resource once ready

if __name__ == '__main__':
    app.run(debug=True)