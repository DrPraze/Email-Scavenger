from bs4 import BeautifulSoup
import requests
import requests.exceptions
import urllib.parse
from collections import deque
import re
import mimetypes
from validate_email_address import validate_email
import socket, threading
import importlib


def search_url(user_url, client_socket):
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
            client_socket.send(str(leads).encode('utf-8'))

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

# def scrapeGoogleMap():
#     task = "scraper"
#     Task = importlib.import_module(task).Task
#     t = Task()
#     t.begin_task()

# Function to handle each client connection
def handle_client(client_socket):
    while True:
        # Receive data from the client
        data = client_socket.recv(1024).decode('utf-8')
        if not data:
            break

        # Process the data using the function
        # results = process_message(data)

        # Start a new thread to send the results to the client
        send_thread = threading.Thread(target=search_url, args=(data, client_socket))
        send_thread.start()

    client_socket.close()

# Main function to start the server
def main():
    host = '127.0.0.1'
    port = 12345

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"[*] Listening on {host}:{port}")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"[*] Accepted connection from {addr[0]}:{addr[1]}")
        
        # Create a new thread to handle the client
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()

if __name__ == "__main__":
    main()
      
