import smtplib
import os

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_id_email(address, client_id):
	# me == my email address
	# you == recipient's email address
	me = "apis@brown.edu"

	# Create message container - the correct MIME type is multipart/alternative.
	msg = MIMEMultipart('alternative')
	msg['Subject'] = "Your Brown APIs Client ID"
	msg['From'] = me
	msg['To'] = address

	# Create the body of the message (a plain-text and an HTML version).
	text = "Welcome to the Brown APIs developer community!\nYour Client ID is: " + client_id + "\nBe sure to include it in every request!\n\nJoin the developer community on Facebook: https://www.facebook.com/groups/brown.apis/"
	html = """\
	<html>
	  <head></head>
	  <body>
	    <p>Welcome to the Brown APIs developer community!</p>
	    <p>Your Client ID is: <em>""" + client_id + """</em>. Be sure to include it in every request you make!</p>
	    <p>Also, be sure to join our <a href="https://www.facebook.com/groups/brown.apis/">community of developers</a> on Facebook.</p>
	  </body>
	</html>
	"""

	# Record the MIME types of both parts - text/plain and text/html.
	part1 = MIMEText(text, 'plain')
	part2 = MIMEText(html, 'html')

	# Attach parts into message container.
	# According to RFC 2046, the last part of a multipart message, in this case
	# the HTML message, is best and preferred.
	msg.attach(part1)
	msg.attach(part2)

	# Send the message via local SMTP server.
	s = smtplib.SMTP(os.environ['POSTMARK_SMTP_SERVER'])
	# sendmail function takes 3 arguments: sender's address, recipient's address
	# and message to send - here it is sent as one string.
	s.sendmail(me, address, msg.as_string())
	s.quit()

send_id_email('joseph_engelman@brown.edu', 'your-client-id-here')