import httpx
import requests

url = "http://127.0.0.1:8000/load-emails"

data = {
    "email":'',
    "password":'',
}

response = httpx.post(url, json=data)

print(f'Status Code: {response.status_code}')
if response.content:
    try:
        print('JSON Response: ', response.json())
    except ValueError:
        print('Response Content is not JSON, raw content: ', response.text)
else:
    print('No Response Content')
