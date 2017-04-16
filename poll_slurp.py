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
from proxylist import ProxyList
from stem import Signal
from stem.util import term
from stem.control import Controller
from termcolor import colored, cprint
from BeautifulSoup import BeautifulSoup
from http_request_randomizer.requests.proxy.requestProxy import RequestProxy
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
#proxies = { 'http': 'socks5h://127.0.0.1:{}'.format(PROXY_PORT),
        #'https': 'socks5h://127.0.0.1:{}'.format(PROXY_PORT) }



def push_vote(poll, option, proxy):
    s = requests.Session()
    choose_useragent();
    header = {'Referer': URL + str(poll) + '/', 'Accept':
    'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'User-Agent': currentAgent, 'Upgrade-Insecure-Requests': '1',
    'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en-US,en;q=0.8'}
    s.headers.update(header)
    built_proxy = { 'http': proxy, 'https': proxy}
    response = s.get(URL + str(poll) + "/", verify=False, proxies=built_proxy,
            timeout=10)
    c = response.content
    soup = BeautifulSoup(c)
    samples = soup.find("a", class_var).attrs
    hidden_pz = soup.find(type="hidden").attrs
    pz = hidden_pz[2][1]
    key_dict_container = samples[1]
    key_dict = ast.literal_eval(key_dict_container[1])
    key_dict['pz'] = str(pz)
    vote_URL = build_URL(key_dict, poll, option)
    vote_response = s.get(vote_URL, verify=False, proxies=built_proxy,
            timeout=10)
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
# requirements.txt
#start_tor(USE_TORRC)

start = time.time()
req_proxy = RequestProxy()
print "Initialization took: {0} sec".format((time.time() - start))
proxies = req_proxy.get_proxy_list()
print " ALL = ", proxies
proxy_list_length = len(req_proxy.get_proxy_list())
print "Size : ", proxy_list_length



for x in range(250,proxy_list_length):
    try:
        output = push_vote(POLL_NUM, POLL_OPTION, proxies[x])
    except requests.exceptions.ProxyError:
        cprint("Dead Proxy :(", 'red', 'on_white')
    except requests.exceptions.ConnectionError:
        cprint("Proxy can't talk to PollDaddy :(", 'red', 'on_white')
    except AttributeError:
        cprint("Proxy request timed out :(", 'red', 'on_white')
    else:
        pass
        revote_status = "revoted" in output.url
        #print output.url
        if "voted" in output.url:
            if (revote_status == 0):
                cprint("Vote number {} successfully submitted!".format(vote_num),
                        'green')
                vote_num += 1
            else:
                cprint("Locked out - renewing Tor exit node...", 'red')
        else:
            cprint("Locked out - renewing Tor exit node...", 'red')
# test_url = 'http://ipv4.icanhazip.com'
#
# while True:
#     start = time.time()
#     request = req_proxy.generate_proxied_request(test_url)
#     print "Proxied Request Took: {0} sec => Status: {1}".format((time.time() - start), request.__str__())
#     if request is not None:
#         print "\t Response: ip={0}".format(u''.join(request.text).encode('utf-8'))
#
#         output = push_vote(POLL_NUM, POLL_OPTION)
#         revote_status = "revoted" in output.url
#         print output.url
#         if "voted" in output.url:
#             if (revote_status == 0):
#                 cprint("Vote number {} successfully submitted!".format(vote_num),
#                         'green')
#                 vote_num += 1
#         else:
#             cprint("Locked out - renewing Tor exit node...", 'red')
#     print "Proxy List Size: ", len(req_proxy.get_proxy_list())
#
#     print"-> Going to sleep.."
#     time.sleep(1)






