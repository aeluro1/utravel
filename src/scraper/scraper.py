# ta
# use http2, set user-agent, data stored in <script> via graphql
import re
import json

def extract_page_manifest(html):
    """Extract JS pageManifest object's state data from graphql hidden in HTML page

    Args:
        html (_type_): _description_
    """
    data = re.findall(r"pageManifest:({.+?})};", html, re.DOTALL)[0]
    return json.loads(data)

print("hello")