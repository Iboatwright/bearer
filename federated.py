#federated.py
import json
import selenium
from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
import time
from urllib.parse import unquote
from urllib.parse import quote
import requests

# add some headless options
options = Options()
options.headless = True
options.add_experimental_option("excludeSwitches",["ignore-certificate-errors"])

# using chrome to access web
driver = webdriver.Chrome(chrome_options=options)

# Open webpage
driver.get('https://my.saml.com?LoginToRP=my.anypoint.mulesoft.com')

time.sleep(2)
# select username box
id_box = driver.find_element_by_id('userNameInput')

# enter username
id_box.send_keys('username')

# select password box
pass_box = driver.find_element_by_id('passwordInput')

# enter password
pass_box.send_keys('password')

# select Sign in box
signIn_button = driver.find_element_by_id('submitButton')

# click Sign in button
signIn_button.click()

# find the proper response header and use it to get the bearer token
for request in driver.requests:
  if request.response and request.path == "https://anypoint.mulesoft.com/accounts/login/receive-id":

    # convert from binary to string and strip leading text
    samlResponse = unquote(str(request.body,'utf-8'))[13:]
    
    # get the bearer token
    url = 'https://anypoint.mulesoft.com/accounts/login/receive-id'
    body = '{"SAMLResponse": "%s"}' % samlResponse 
    headers = {
      'Content-Type': 'application/json',
      'X-Requested-With': 'XMLHttpRequest'
    }
    req = requests.post(url, data=body, headers=headers)
    
    # extract the bearer token from the json response
    bearer=json.loads(req.text)['access_token']

    # write the bearer token to a file in the .anypoint folder
    fo = open("~/.anypoint/bearer", "w")
    fo.write(bearer)
    fo.close()

    # print the bearer token to the commandline without a new line character
    print(bearer, end = '')