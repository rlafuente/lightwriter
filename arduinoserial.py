#!/usr/bin/python

# Script for sending text data to an Arduino board
# Used for the Lightwriter piece

# It accepts a single string as a parameter;
# This string should be piped in from the console using the
# lw-parsestring script, like this:
#   python lw-parsestring "bright happy flowers" | python lw-sendstring

# This script uses a small, hastily put-together network protocol;
# It sends an int and Arduino is supposed to confirm it got it,
# by sending back the same value.
# The signals used and their values are:
# 0 - Write "0" value
# 1 - Write "1" value
# 2 - HELLO/OK signal (used in startup and after copying each character)
# 3 - Wrap-up and finish
LEDON = '0'
LEDOFF = '1'
HELLO = '2'
GOODBYE = '3'



import serial
import sys

position = 0 					# keeps track of where we are in the string to send
sendok = False 					# toggle for knowing if it's ok to send data
finished = False 				# will be true when everything is parsed
string = sys.argv[1].strip("\n") 	# get input from stdin

# print string

# added timeout for making sure we aren't left hanging
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)

print
print "Attempting HELLO with Lightwriter... (if this doesn't change for 2 seconds, it crashed)"

# send HELLO signal - checks if arduino is alive
while 1:
	ser.write(HELLO);
	token = ser.readline()
	if (token[0] == HELLO):
		break
	print "Token doesn't seem right..."

print "  Lightwriter says hello, beginning transfer!"
print

while 1:
	if sendok: # did we receive an ok for the arduino for going on?
		if finished: # are we at the end?
			print "Finishing..."
			# wrap up and finish
			ser.write(GOODBYE)
			data = ser.readline()
			ser.flush()
			if (data[0] == GOODBYE):
				print "All done, Lightwriter looks happy :)"
				print
				break
			else:
				print "Finished, but Lightwriter is complaining :/"
				print
				break	
		
		# if it's not finished, send next byte
		print "Sending next byte (position " + str(position) + ", value "+ string[position ]+ "):"
		ser.write(string[position]);
		data = ser.readline()
		# now check if the arduino got it
		if (data[0] != LEDON and data[0] != LEDOFF): # is it the right signal?
			print "Lightwriter says it didn't understand (says " + data[0] + "), sending data again..."
			ser.write(string[position]);
			data = ser.readline()
							
		print "Lightwriter confirms it received " + data[0] + "..."
		# set the flag to false so that we'll wait for the next arduino ok
		sendok = False 
		# move one step ahead
		position = position + 1
		# test for next value, if it doesn't exist the string is over
		# so send a null character (required by arduino to form a correct
		# string) and finish
		if (position == len(string)):
			finished = True
		
	# if HELLO is not ok, poke the arduino again to check for a response
	ser.flush()
	ser.write(HELLO);		
	data = ser.readline() # read incoming data
#	print data
	if (data[0] == HELLO): # check if we got anything from the arduino; we're expecting "2" = all ok
		sendok = True # it's ok to send the next packet
		print
		print "Lightwriter says all OK so far :D"
	else: # try sending it again
		ser.flush()
		print "Didn't receive confirmation, retrying...\n"
		ser.write(HELLO);		
		data = ser.readline()
		if (data[0] == HELLO): # did we get it right now?
			sendok = True # if so, phew
		else: # otherwise it's okay, try again
			print "Lightwriter doesn't acknowledge reception :( let's pester it some more and see if it works"
