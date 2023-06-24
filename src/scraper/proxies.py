import re
import requests
from lxml import etree

## HTTP proxies method

r = r"([0-9]+(?:\.[0-9]+){3}:[0-9]+)"
response = requests.get("https://spys.me/proxy.txt")
text = response.text
proxies = re.findall(r, text)

response = requests.get("https://free-proxy-list.net/")
tree = etree.HTML(response.text, None)
text = tree.xpath("//textarea/text()")
for t in text:
    proxies_temp = re.findall(r, t)
    proxies.extend(proxies_temp)
    
print(proxies)

## SOCKS (Tor) proxies method
# https://boredhacking.com/tor-webscraping-proxy/