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
* this is an early version of the script I which just processed federated a single hard-coded federated Id.

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
The simplist use before install is `python3 bearer.py -u username -p password`. After install is `bearer`.
### side-effects/non-obvious features
#### -offline
skips 


## Example usage
### (1) *`bearer`*
* uses the default profile to get a token.
* the token is written to stdout and saved to the `token` file

### (1.1) *`bearer -o`*
