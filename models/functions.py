# -*- coding: utf-8 -*-

import datetime

## IPN -> Paypal Logs

def log_in_file(msg, path="/tmp/ipngenerallog.txt"):
	with open(path, 'a') as log:
		now = datetime.datetime.now()

		log.write('\n'+now.strftime('%m/%d/%Y - %H:%M:%S')+'\n'+msg+'\n')

def write_logs(request):
	message = "-" * 80
	message += "\nIPN Received\n"
	message += "ARGS: \n" + str(request.args) + "\n"
	message += "VARS: \N" + str(request.vars) + "\n"
	log_in_file(message)

def generate_tokens(token_class, ammount):
	return float(ammount)/2.5