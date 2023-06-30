from bs4 import BeautifulSoup
import requests
import requests.exceptions
import urllib.parse
from collections import deque
import re
import mimetypes
from validate_email_address import validate_email

from flask import Flask, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
import importlib


def search_url(user_url, room):
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

            #share retreived email on live feed
            leads = {}
            for item in emails:
              if validate_email(item):
                leads[item] = {"status":"Verified"};
              else:
                leads[item] = {"status":"Invalid"};
            send_email_leads(room, leads)

            soup = BeautifulSoup(response.text, features="lxml")

            for anchor in soup.find_all("a"):
              link = anchor.attrs['href'] if 'href' in anchor.attrs else ''
              if link.startswith('/'):
                link = base_url + link
              elif not link.startswith('http'):
                link = path + link
              if not link in urls and not link in scraped_urls:
                urls.append(link)
        except Exception as e:
          print(f"An error occured{e}");
  except KeyboardInterrupt:
    print('[-] Closing!')

  for mail in emails:
    print(mail)
    # return mail
    return emails

def scrapeGoogleMap():
    task = "scraper"
    Task = importlib.import_module(task).Task
    t = Task()
    t.begin_task()

app = Flask(__name__)
socketio = SocketIO(app)

@socketio.on('connect')
def handle_connect():print("A client is connected.")

@socketio.on('disconnect')
def handle_disconnect():print("A client is disconnected.")

@socketio.on('join_room')
def handle_join_room(data):
  room = data['room']
  join_room(room)
  print(f"A client joined room: {room}")

@socketio.on('leave_room')
def handle_leave_room(data):
  room = data['room']
  leave_room(room)
  print(f"A client left room: {room}")

@socketio.on('search')
def handle_search(data):
  query = data['query']
  room = data['room']
  search_type = data['searchType']

  if search_type == "google_maps":
    # email_leads = google_maps_search(query)
    pass
  elif search_type == 'url':
    search_url(query)
  else:
    # email_leads = []
    pass

def send_email_leads(room, email_leads):socketio.emit('email_leads', email_leads, room=room)

if __name__=='__main__':
  socketio.run(app, host='0.0.0.0', port=5000)