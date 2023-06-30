import requests

BASE = "http://127.0.0.1:5000/search"
response = requests.post(BASE, json={"query":"https://slakenet.com.ng/","room":"emailroom"});
print(response.json())