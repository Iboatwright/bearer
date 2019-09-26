# bearer Mulesoft authentication automation tool
## tl;dr -- just get me started
* *`pip3 install plac selenium selenium-wire`*
* download [ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver/downloads) for Selenium and install (copy) it to `/usr/local/bin/`. (or anywhere in your system PATH)
* edit `profiles` and add your account info
* edit `bearerConfig.py` and update the CONFIG variables
* edit `bearer.py` and update the `CONFIG_FILE_PATH` to the folder you plan to store the `bearerConfig.py` file in.
* move `profiles` and `bearerConfig.py` to the folders you specified.
* make `bearer.py` executable. *`chmod +x bearer.py`*
* move `bearer.py` to `~/.local/bin/`.
  * optionally rename `bearer.py` to just `bearer`

> If it doesn't work after this you've probably got a slightly different setup than mine.

## Whyisit?
I made this tool to simplify my life. This was written to work on Ubuntu 19.04 with the default installs of [Plac](http://micheles.github.io/plac/), [Selenium](https://pypi.org/project/selenium/) and [Selenium Wire](https://pypi.org/project/selenium-wire/) via pip3. I'm using the Chrome driver for Selenium which can be found [here](https://sites.google.com/a/chromium.org/chromedriver/downloads). I don't know if this tool will work with another driver. Most of this tool should easily port to other platforms, but YMMV. 

## Whatisit?
This is a python 3 tool to help automate getting Mulesoft bearer authorization tokens. It works for both federated and non-federated ids. The federated id portion relies on selenium. It could be done without it, but this way got the tool working faster. I used Plac to simplify the cli boilerplate code. It's not fundamental to the tool, but removing it requires some refactoring (mostly commandline argument handling).

## Whatarethefilesfor?
### **profiles**
* contains a JSON object of named profiles. Only username, password, and federated attributes are implemented. 
* It's trivial to add more attributes. Look for the `# Profile processing` comment in bearer.py.
* profiles is only processed when no *username* is supplied.
* I store this file in my `~/.anypoint` folder. Since it'll have sensitive account details you'll want to keep it safe.

### **bearerConfig**
* a python file with a map of variables that I wanted to be able to change easily without editing bearer
* Just copy the contents of this file. Look for the `# CONFIG = {}` comment in bearer.py.
* I also stored this file in `~/.anypoint`. If you store it anywhere else, you will need to update the `CONFIG_FILE_PATH` at the head of the bearer.py file.

### **bearer**
* the python3 script that does the work
* I just copy this into `~/.local/bin/` and remove the .py extension. You might need to *`chmod +x bearer`* to make it executable.

### **extra/federated.py**
* this is an early version of the script which processed a single hard-coded federated Id.

### **token** *aka savedBearerToken*
* after a token is successfully acquired it is saved to a plain text file (default is `~/.anypoint/token`).
* running *`bearer -o`* will then read the token from the file instead of getting a new token.

## Howsitwork?
Here's the output of *`bearer -h`*:
```
usage: bearer [-h] [-offline] [-newline] [-federated] [-username USERNAME]
              [-password PASSWORD] [-P default] [-verbosity 4]

A tool to get a Mulesoft authentication bearer token

optional arguments:
  -h, --help            show this help message and exit
  -offline              Does not make API calls, reads the token from a file
  -newline              append newline terminator to token output
  -federated            process as a federated Id
  -username USERNAME    username
  -password PASSWORD    password
  -P default, --profile default
                        Stored profile to use
  -verbosity 4          Level of output to display, 0=none
```
> See the [Plac](http://micheles.github.io/plac/) documentation for more about argument handling.
There's some minor setup needed to get it working. 
The simplist use before install is *`python3 bearer.py -u username -p password`*. After install it cuts down to *`bearer`*.
### side-effects/non-obvious features
argument       | effect
-------------- | ------
*-offline*     | reads token from the `token` file and skips all other processing
*-newline*     | appends a `"\n"` string to the token when written to stdout. By default the token is written to stdout without a newline character.
*-username*    | if a username is supplied then profiles are not processed.
*-verbosity 0* | This causes the `token` file to be silently updated. I added it for asynchronous use. (it's still blocking so you'd have to spin it off on it's own)


## Example usage
### (1) *`bearer`*
* uses the default profile to get a token.
* the token is written to stdout and saved to the `token` file
* notice the lack of newline
```
jack@ubuntu:~$ bearer
4c5a1793-e2dd-4353-8dca-5e594a551af1jack@ubuntu:~$ 
```

### (1.1) *`bearer -o -n`*
* reads the last token from the `token` file
```
jack@ubuntu:~$ bearer -o -n
4c5a1793-e2dd-4353-8dca-5e594a551af1
jack@ubuntu:~$ 
```

### (2) *`bearer -federated -n -username jack@ubuntu -password drowssap`*
```
jack@ubuntu:~$ bearer -federated -n -username jack@ubuntu -password drowssap
4c0dc090-9906-4236-bc17-93ca5862e801
jack@ubuntu:~$ 
```

### (3) *`bearer -username jack@ubuntu -password wrongPassword`*
* example of `-verbosity 4` (current max) error output
```
jack@ubuntu:~/code/bearer$ bearer -username jack@ubuntu -password wrongpassword
401
{'Date': 'Mon, 23 Jan 2019 21:18:31 GMT', 'Expires': '-1', 'Pragma': 'no-cache', 'Server': 'nginx', 'Set-Cookie': '_csrf=s2iakagWQHb7q6k9TkkaJlzl; Path=/; HttpOnly; Secure, XSRF-TOKEN=ccUV9KG0-tYNXMB8SPa2c2PGmTnn; Path=/; Secure, mulesoft.sess=eyJpZCI6IkoczTEhzTU5VeWRBUtyc3o5In0=; path=/; secure; httponly, mulesoft.sess.sig=RsLbJBuMimK4bWQzHA; path=/; secure; httponly', 'Strict-Transport-Security': 'max-age=31536000; includeSubDomains', 'Vary': 'X-HTTP-Method-Override', 'WWW-Authenticate': 'login failed', 'X-ANYPNT-TRX-ID': '7efc0260', 'X-Content-Type-Options': 'nosniff', 'X-DNS-Prefetch-Control': 'off', 'X-Download-Options': 'noopen', 'X-Frame-Options': 'SAMEORIGIN, SAMEORIGIN', 'X-RateLimit-Limit': '150', 'X-RateLimit-Remaining': '149', 'X-RateLimit-Reset': '1569993520', 'X-XSS-Protection': '1; mode=block', 'Content-Length': '13', 'Connection': 'keep-alive'}
Unauthorized
jack@ubuntu:~/code/bearer$ 
```

## Potential issues
* If you are getting 401 errors the problem might be with the format of the SAML response from your organization's IDP single sign on page. Use the steps on [this](https://docs.mulesoft.com/access-management/troubleshoot-saml-assertions-task) page to get a copy of the saml output. Then you can alter the `bearer.getFederatedRequestParams()` method's `samlResponse = unquote(str(request.body,'utf-8'))[13:]` variable to match the expected format.