#!/usr/bin/env python

MAILFILE = 'test-emails.txt'

print 'Give me your e-mail address:'
email = raw_input('>> ')

mailfile = open(MAILFILE, 'a')
mailfile.write('    %s\n' % email)
mailfile.close()

