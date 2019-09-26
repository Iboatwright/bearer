#!/usr/bin/python3
import plac
import json
import sys
import os.path

# CONFIG = {}  # config can be moved into the main file here. just remove the below CONFIG import.
CONFIG_FILE_PATH=os.path.expanduser("~/.anypoint/")

if os.path.isfile(CONFIG_FILE_PATH + "bearerConfig.py"):
  sys.path.append(CONFIG_FILE_PATH)
from bearerConfig import CONFIG

@plac.annotations(
  offline=plac.Annotation("Does not make API calls", 'flag'),
  newline=plac.Annotation("append newline terminator to output", 'flag'),
  federated=plac.Annotation("is FederatedId", 'flag'),
  username=plac.Annotation("mule username", 'option'),
  password=plac.Annotation("password", 'option'),
  profile=plac.Annotation("Stored profile to use", 'option', 'P'),
  verbosity=plac.Annotation("Level of output to display, 0=none", 'option', type=int))
def main(offline, newline, federated, username, password, profile=CONFIG['defaultProfile'], verbosity=CONFIG['verbosity']):
  "A tool to get a mulesoft authentication bearer token"

  newline = "\n" if newline else ""

  if offline:
    fo = open(CONFIG['pathToSavedBearerToken'], "r")
    yield [fo.read(), newline]
    fo.close()
    exit(0)

  # Profile processing
  if not username: 
    fo = open(CONFIG['pathToStoredProfiles'], "r")
    account=json.loads(fo.read())[profile]
    fo.close()
    username=account['username']
    password=account['password']
    federated=account['federated'] if 'federated' in account else False

  # these methods return a tuple with (url, headers, body)
  if federated:
    url, headers, body = getFederatedRequestParams(username, password, CONFIG['samlUrl'])
  else:
    url, headers, body = getAnypointRequestParams(username, password)

  # late import to avoid cost overhead if offline... maybe
  import requests
  req = requests.post(url, headers=headers, data=body)

  # process the response
  if req.status_code == 200:
    # extract the bearer token from the json response
    bearer=json.loads(req.text)['access_token']

    # write the bearer token to a file in the .anypoint folder
    fo = open(CONFIG['pathToSavedBearerToken'], "w")
    fo.write(bearer)
    fo.close()
    if verbosity >= 1:
      yield [bearer, newline] # if not newline print(string, end="")
      
  # request failed 
  else:
    # print the error details if verbosity level is greater than zero
    if verbosity >= 1:
      yield "%s" % req.status_code
    if verbosity >= 2:
      yield "%s" % req.headers
    if verbosity >= 3:
      yield "%s" % req.text
    exit(1) # exit code is non-zero

# returns request parameters needed to obtain a bearer token from the Anypoint IdP
def getAnypointRequestParams(username, password):
  url = 'https://anypoint.mulesoft.com/accounts/login'
  headers = {'Content-Type': 'application/json'}
  body = """{
    "username": "%s",
    "password" : "%s"
  }""" % (username, password)
  return url, headers, body

# returns request parameters needed to obtain a bearer token from a federated IdP
def getFederatedRequestParams(username, password, samlUrl):
  import selenium
  from seleniumwire import webdriver
  from selenium.webdriver.chrome.options import Options
  import time
  from urllib.parse import unquote
  from urllib.parse import quote

  # add some headless options
  options = Options()
  options.headless = True
  options.add_experimental_option("excludeSwitches",["ignore-certificate-errors"])

  # using chrome to access web pages
  driver = webdriver.Chrome(chrome_options=options)

  # Open federated authentication webpage that returns the needed saml response
  driver.get(samlUrl)

  time.sleep(2)  # waiting for the page to load
  # select username box
  id_box = driver.find_element_by_id('userNameInput')

  # enter username
  id_box.send_keys(username)

  # select password box
  pass_box = driver.find_element_by_id('passwordInput')

  # enter password
  pass_box.send_keys(password)

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

  # close the chrome browser instance
  driver.quit()

  return url, headers, body

if __name__ == "__main__":
  for output in plac.call(main, eager=False):
    if type(output) is str:
      print(output)
    else:
      print(output[0], end=output[1])