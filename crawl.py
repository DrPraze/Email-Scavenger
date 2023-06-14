from bs4 import BeautifulSoup
import requests
import requests.exceptions
import urllib.parse
from collections import deque
import re
import mimetypes

def requests_retry_session(
	retries=3,
	backoff_factor=0.3,
	status_forcelist=(500, 502, 504),
	session=None,
):
	session = session or requests.Session()
	session.max_redirects = 60
	# session.headers['User-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 ' \
	#                                 '(KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'
	retry = Retry(
		total=retries,
		read=retries,
		connect=retries,
		backoff_factor=backoff_factor,
		status_forcelist=status_forcelist,
	)
	adapter = HTTPAdapter(max_retries=retry)
	session.mount('http://', adapter)
	session.mount('https://', adapter)

	return session
	
def get_emails(self, url, session):

    try:
        # sending an http get request with specific url and get a response
        response = session.get(url)

    except requests.exceptions.ConnectionError:
        print("Connection Error " + url)
        return
    except requests.exceptions.HTTPError:
        print("Bad Request. " + url)
        return
    except requests.exceptions.Timeout:
        print("Request timed out" + url)
        return
    except requests.exceptions.TooManyRedirects:
        print("Too many redirects " + url)
        return
    except requests.exceptions.InvalidURL:
        print("Invalid URL. " + url)
        return
    except requests.exceptions.InvalidSchema:
        print("Invalid Schema." + url)
        response = session.get("http://" + url)
    except requests.exceptions.MissingSchema:
        print("Missing Schema URL. " + url)
        response = session.get("http://" + url)
    except requests.exceptions.RetryError:
        print("Retry Error " + url)
        return

    if response is None:
        return
    # email pattern to match with - name@domain.com
    email_pattern = "[a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9._-]+" # 1st pattern
    # making the regex workable - compile it with ignore case
    email_regex = re.compile(email_pattern, re.IGNORECASE)
    # match all the email in html response with regex pattern and get a set of emails
    # response.text returns html as string
    email_list = email_regex.findall(response.text)

    # email pattern to match with - name @ domain.com
    email_pattern = "[a-zA-Z0-9._-]+\s@\s[a-zA-Z0-9._-]+\.[a-zA-Z0-9._-]+" # 2nd pattern
    # making the regex workable - compile it with ignore case
    email_regex = re.compile(email_pattern, re.IGNORECASE)
    # match all the email in html response with regex pattern and get a set of emails
    # response.text returns html as string
    email_list.extend(email_regex.findall(response.text))

    # email pattern to match with - name at domain.com
    email_pattern = "[a-zA-Z0-9._-]+\sat\s[a-zA-Z0-9._-]+\.[a-zA-Z0-9._-]+" # 3rd pattern
    # making the regex workable - compile it with ignore case
    email_regex = re.compile(email_pattern, re.IGNORECASE)
    # match all the email in html response with regex pattern and get a set of emails
    # response.text returns html as string
    email_list.extend(email_regex.findall(response.text))

    return set(self.strip(email_list))

def strip(self, all_email):
    first = [item.replace(" at ", "@") for item in all_email]
    second = [item.replace(" AT ", "@") for item in first]
    third = [item.replace(" @ ", "@") for item in second]

    return third

def start_from_google(query):
  query = query+" email"
  query = "+".join(query.split())
  url = "https://www.google.com/search?q={0}".format(query)
  session = requests_retry_session()
  try:
	# sending an http get request with specific url and get a response
	starttime = time.time()
	response = session.get(url)
	if response is None:
	  return
  except requests.exceptions.ConnectionError:
	print("Connection Error " + url)
	return "Connection Error"
  except requests.exceptions.Timeout:
	print("Request timed out" + url)
	return "Request timed out"
  except requests.exceptions.TooManyRedirects:
	print("Too many redirects " + url)
	return
  except requests.exceptions.HTTPError:
	print("Bad Request." + url)
	return
  except requests.exceptions.InvalidURL:
	print("Invalid URL. " + url)
	return
  except requests.exceptions.InvalidSchema:
	print("Invalid Schema." + url)
	return
  except requests.exceptions.MissingSchema:
	print("Missing Schema URL. " + url)
	return
  except requests.exceptions.RetryError:
	print("Retry Error " + url)
	return

  soup = BeautifulSoup(response.text, 'lxml')

  all_email = []
  for tag in soup.find_all('cite'):
	url = tag.get_text()
	emails = self.get_emails(url, session)
	if emails is None:
	  continue
	all_email.extend((emails, url))

  endtime = time.time()
  return all_email, (endtime - starttime)

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
	return mail
		  