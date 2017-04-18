# PollDaddySlurp
Automatically cast PollDaddy.com votes using Tor anonymity, Russians-for-Trump style.

###To Do:

- update program to accept poll number and vote id on `STDIN`

- fetch poll information and display poll name, potential options, and current
  vote count

- integrate finding IP's asynchronously with the voting process
    - update proxybroker python library to check source proxy listings and
      avoid dead or down links

- potentially remove proxybroker dependency altogether, or add requirements.txt
  mandating a modified version of the proxybroker library
