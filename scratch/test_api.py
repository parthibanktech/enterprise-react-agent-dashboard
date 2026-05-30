import urllib.request
import urllib.error
import json

url = "http://127.0.0.1:8000/api/chat"
payload = {
    "message": "Which products have a price greater than 200?",
    "history": [],
    "live": True
}

req = urllib.request.Request(
    url,
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"},
    method="POST"
)

try:
    response = urllib.request.urlopen(req)
    print("SUCCESS 200 OK:")
    print(response.read().decode())
except urllib.error.HTTPError as e:
    print("ERROR 500:")
    print(e.read().decode())
except Exception as e:
    print("OTHER ERROR:", e)
