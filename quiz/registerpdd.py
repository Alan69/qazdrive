import requests
import json
import re

# def login_to_pdd(username, password):
#     url = "https://api.pddtest.kz/auth/authorize"
#     url_main_page = "https://pddtest.kz/main"
#     with requests.Session() as s:
#         # s.get(url)
#         # csrftoken = s.cookies['csrftoken']
#         payload = {'username': username, 'password': password}
#         res = s.post(url, json=payload)
#         s.headers.update({'Authorization': 'Bearer ' + json.loads(res.content)['access_token'][0]})
#         r = s.get(url_main_page)
#         print(res.content)
#         print(r.content)
#         return s

# login_to_pdd('admin159@mail.com', '7672WQqR')

# Set the URL and form data for the login page
login_url = 'https://pddtest.kz/auth'
form_data = {
    'username': 'admin159@mail.com',
    'password': '7672WQqR'
}

# Send a GET request to the login page to retrieve the form data and authentication tokens
response = requests.get(login_url)

# Extract the necessary form data and authentication tokens from the login page
# For example, you could use a regular expression to match the values of hidden form fields

token_regex = re.compile(r'<input type="hidden" name="token" value="(.+?)"')
match = token_regex.search(response.text)
token = match.group(1) if match else None

# Add the form data and authentication tokens to the form data object
form_data['token'] = token

# Send a POST request to the login page with the form data and authentication tokens
response = requests.get(login_url, data=form_data)
print(response.text)
# Check if the login was successful
# if response.status_code == 200:
#     # Login was successful. You can now access the protected content
#     print(response.text)
# else:
#     # Login was unsuccessful
#     print('Error: Login failed')