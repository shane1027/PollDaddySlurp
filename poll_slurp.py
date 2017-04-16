#!/usr/bin/env python2.7

#######################
# author: Shane Ryan  |
# release: April 2017 |
###############################################################################
# requires Tor to be listening on localhost:9050 --> control port on 9051     |
# https://wiki.archlinux.org/index.php/tor     (set control port pass below)  |
# TorCtl lib available @ https://github.com/aaronsw/pytorctl   (pip install)  |
###############################################################################

import requests, warnings, time, random, io
import stem.process
from stem import Signal
from stem.util import term
from stem.control import Controller
from termcolor import colored, cprint
from bs4 import BeautifulSoup
import ast      # used to convert string to dict
from requests.packages.urllib3.exceptions import InsecureRequestWarning
# no ssl verification for a voting bot, shush you darn warnings!!
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Voting related variables
URL = 'https://polldaddy.com/poll/'
POLL_NUM = 9720163
POLL_OPTION = 44443196
VOTE_COUNT = 1000
DELAY = None
vote_num = 1

userAgents = []
currentAgent = ""
class_var = "btn btn-primary btn-large vote-button"
vote_ref_url = 'http%3A//sportsradiodetroit.com/2017/04/09/final-four-detroits-favorite-female-personality-contest-2/'
referer = 'http://sportsradiodetroit.com/2017/04/09/final-four-detroits-favorite-female-personality-contest-2/'

# Proxy related variables
oldIP = "0.0.0.0"
newIP = "0.0.0.0"
tor_URL = 'https://check.torproject.org'
PROXY_PORT = 9050
SOCKS_PORT = PROXY_PORT
USE_TORRC = 1
proxies = { 'http': 'socks5h://127.0.0.1:{}'.format(PROXY_PORT),
        'https': 'socks5h://127.0.0.1:{}'.format(PROXY_PORT) }



def push_vote(poll, option):
    s = requests.Session()
    choose_useragent();
    header = {'Referer': URL + str(poll) + '/', 'Accept':
    'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'User-Agent': currentAgent, 'Upgrade-Insecure-Requests': '1',
    'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en-US,en;q=0.8'}
    s.headers.update(header)
    response = s.get(URL + str(poll) + "/", verify=False, proxies=proxies)
    c = response.content
    soup = BeautifulSoup(c)
    samples = soup.find("a", class_var).attrs
    hidden_pz = soup.find(type="hidden").attrs
    pz = hidden_pz[2][1]
    key_dict_container = samples[1]
    key_dict = ast.literal_eval(key_dict_container[1])
    key_dict['pz'] = str(pz)
    vote_URL = build_URL(key_dict, poll, option)
    vote_response = s.get(vote_URL, verify=False, proxies=proxies)
    s.cookies.clear()
    return vote_response

def open_useragents():
    f = open("useragent.txt", "r")
    for line in f:
        userAgents.append(line.rstrip('\n').rstrip('\r'))
    f.close()

def choose_useragent():
    global currentAgent
    k = random.randint(0, len(userAgents)-1)
    currentAgent = userAgents[k]

def print_bootstrap_lines(line):
    if "Bootstrapped " in line:
        print(term.format(line, term.Color.BLUE))

def start_tor(config_state):
    if (config_state):
        tor_process = stem.process.launch_tor_with_config(
          config = {
            'SocksPort': str(SOCKS_PORT),
            'ExitNodes': '{us}',
            'ControlPort': '9051'
          },
          init_msg_handler = print_bootstrap_lines,
        )
    else:
        tor_process = stem.process.launch_tor(init_msg_handler =
                print_bootstrap_lines)

def check_tor():
    try:
        tor_response = requests.get(tor_URL, proxies=proxies)
    except requests.exceptions.ConnectionError:
        print "Couldn't connect to Socks5 service on port {}".format(PROXY_PORT)
        print "Is Tor running?"
        exit(1)
    else:
        if ("Congratulations" in tor_response.text):
            cprint("Connected to the Tor network.", 'green')
        else:
            print "Connected to Socks5 proxy but can't reach the Tor network!"
            exit(1)

def scramble_ip():
    def renew_connection():
        with Controller.from_port(port = 9051) as controller:
            controller.authenticate(password="alpine")
            controller.signal(Signal.NEWNYM)
    global oldIP
    global newIP
    if oldIP == "0.0.0.0":
        renew_connection()
        oldText = requests.get("http://icanhazip.com/", proxies=proxies)
        oldIP = oldText.content.rstrip()
    else:
	oldText = requests.get("http://icanhazip.com/", proxies=proxies)
        oldIP = oldText.content.rstrip()
	renew_connection()
	newText = requests.get("http://icanhazip.com/", proxies=proxies)
        newIP = newText.content.rstrip()
    while oldIP == newIP:
        #time.sleep(3)
    	newText = requests.get("http://icanhazip.com/", proxies=proxies)
        newIP = newText.content.rstrip()
    if (newIP == '0.0.0.0'):
        print "IP address scrambled successfully: {}".format(oldIP)
    else:
        print "IP address scrambled successfully: {}".format(newIP)

def build_URL(sending_keys, poll, option):
    va = sending_keys['at']
    pt = '0'
    r = '0'
    p = poll
    a = option
    t = sending_keys['t']
    token = sending_keys['n']
    pz = sending_keys['pz']
    SEND_URL = "https://polldaddy.com/vote.php?va={}&pt={}&r={}&p={}&a={}%2C&o=&t={}&token={}&pz={}".format(va, pt, r, p, a, t, token, pz)
    return SEND_URL



open_useragents()
##TODO: check if Tor is already running and return that as process id, or
## terminate the process and start a new one
#start_tor(USE_TORRC)
check_tor()
scramble_ip()
for x in range(0, VOTE_COUNT+1):
    output = push_vote(POLL_NUM, POLL_OPTION)
    vote_status = "revoted" in output.url
    print output.url
    if (vote_status == 0):
        cprint("Vote number {} successfully submitted!".format(vote_num),
                'green')
        vote_num += 1
        scramble_ip()
    else:
        cprint("Locked out - renewing Tor exit node...", 'red')
        scramble_ip()





#http://polls.polldaddy.com/vote-js.php?p=9720163&b=2&a=44443196,&o=&va=0&cookie=0&n=3e6ac658d5|306&url=http%3A//sportsradiodetroit.com/2017/04/09/final-four-detroits-favorite-female-personality-contest-2/

#https://polldaddy.com/vote.php?va=10&pt=0&r=2&p=9720163&a=44443196%2C&o=&t=1100&token=a4e582f5d0aceb058a4e72c2dbac0cd6&pz=97


#   GET /vote.php?va=10&pt=0&r=2&p=9720163&a=44443196%2C&o=&t=1100&token=a4e582f5d0aceb058a4e72c2dbac0cd6&pz=979 HTTP/1.1
#   Host: polldaddy.com
#   User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:51.0) Gecko/20100101 Firefox/51.0
#   Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
#   Accept-Language: en-US,en;q=0.5
#   Accept-Encoding: gzip, deflate, br
#   Referer: https://polldaddy.com/poll/9720163/
#   Cookie: __utma=182033702.54197870.1492119988.1492119988.1492119988.1; __utmz=182033702.1492119988.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmc=182033702; __utmb=182033702.1.10.1492119988; PD_REQ_AUTH=ebf4ec5fc85249d0ea0c90e24550268e; __utmt=1; __utmt_b=1; PDjs_poll_9720163_1=1492120016196
#   Connection: keep-alive
#   Upgrade-Insecure-Requests: 1





# GET /vote-js.php?p=9720163&b=2&a=44443196,&o=&va=0&cookie=0&n=3e6ac658d5|306&url=http%3A//sportsradiodetroit.com/2017/04/09/final-four-detroits-favorite-female-personality-contest-2/ HTTP/1.1
# Host: polls.polldaddy.com
# User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:51.0) Gecko/20100101 Firefox/51.0
# Accept: */*
# Accept-Language: en-US,en;q=0.5
# Accept-Encoding: gzip, deflate
# Referer: http://sportsradiodetroit.com/2017/04/09/final-four-detroits-favorite-female-personality-contest-2/
# Cookie: __utma=182033702.1741471858.1492119006.1492119006.1492119006.1; __utmz=182033702.1492119006.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); PD_poll_9720163_1=1492099887; __utmc=182033702; PD_REQ_AUTH=a564aeec55fce15ff21e2d537693b077; __utmb=182033702.1.10.1492119006; __utmt=1; __utmt_b=1
# Connection: keep-alive


# GET /vote.php?va=10&pt=0&r=0&p=9720163&a=44443196%2C&o=&t=36024&token=4a8fb3264f2893dfe896167f80d621b3&pz=17 HTTP/1.1
# Host: polldaddy.com
# User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:51.0) Gecko/20100101 Firefox/51.0
# Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
# Accept-Language: en-US,en;q=0.5
# Accept-Encoding: gzip, deflate, br
# Referer: https://polldaddy.com/poll/9720163/
# Cookie: __utma=108186013.1171067445.1491972247.1491972247.1491972247.1; __utmb=108186013.1.9.1491972247; __utmz=108186013.1491972247.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmc=108186013; PD_REQ_AUTH=3dcf2b0280f55bd18d0ac8c1cf20e8c3; __utmt=1; __utmt_b=1
# Connection: keep-alive
# Upgrade-Insecure-Requests: 1

