#! /usr/bin/env python
import DNS
import optparse

MyKey = "LkoE8fh7Lw2hRcw0uNR6iX4QZoBjtaAV"

DNS.ParseResolvConf()
d = DNS.Request()

def main():
	p = optparse.OptionParser()
	p.add_option('--message', '-m', default="Hello")
	p.add_option('--key', '-k', default=MyKey)
	options, arguments = p.parse_args()
	message = options.message
	key = options.key
	message += "." + key
	message += ".twns.eu"
	DNS.ParseResolvConf()
	d = DNS.Request()
	res = d.req(name=message)
	print "Sent: " + message

if __name__ == '__main__':
    main()
