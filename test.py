import httpx
import requests

url = "http://127.0.0.1:8000/load-emails"  # replace 'your-endpoint' with the real one

data = {
    "email":'suluguni1988@gmail.com',
    "password":'mmxz xsqq zuzu uqnd',
}

response = httpx.post(url, json=data)

print(f'Status Code: {response.status_code}')
if response.content:
    # Attempt to print JSON only if there is content in the response
    try:
        print('JSON Response: ', response.json())
    except ValueError:
        print('Response Content is not JSON, raw content: ', response.text)
else:
    print('No Response Content')