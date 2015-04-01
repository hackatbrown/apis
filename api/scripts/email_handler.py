import smtplib
import os

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_id_email(address, firstname, client_id):
	# me == my email address
	# you == recipient's email address
	me = os.environ['GMAIL_USER']

	# Create message container - the correct MIME type is multipart/alternative.
	msg = MIMEMultipart('alternative')
	msg['Subject'] = "Your Brown APIs Client ID"
	msg['From'] = me
	msg['To'] = address

	# Create the body of the message (a plain-text and an HTML version).
	text = "Hi, " + firstname + "! Welcome to the Brown APIs developer community.\nYour Client ID is: " + client_id + ". Be sure to include it in every request!) You can use this Client ID for multiple projects. There is currently a maximum of one Client ID per student, but exceptions can be made on a case-by-case basis.\n\nJoin the developer community on Facebook: https://www.facebook.com/groups/brown.apis/\n\nHappy developing!\nThe Brown APIs Team\n"
	html = """\
	<html>
	  <head>
	  	<style>
			p {
			    font-size: 14px;
			} 
			.center {
				margin: auto;
				text-align: center;
			}
		</style>
	  </head>
	  <body>
	    <h2 class="center">Hi, """ + firstname + """! Welcome to the Brown APIs developer community.</h2>
	    <p>Your Client ID is: <em>""" + client_id + """</em>.</p>
	    <p>Be sure to include your Client ID with every request you make! You can use this Client ID for multiple projects. Currently, there is a maximum of one Client ID per student, but exceptions can be made on a case-by-case basis.</p>
	    <p>Also, be sure to join our <a href="https://www.facebook.com/groups/brown.apis/">community of developers</a> on Facebook.</p>
	    <br />
	    Happy developing! <br />
	    The Brown APIs Team
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

	s = smtplib.SMTP("smtp.gmail.com", 587)
	s.starttls()
	s.login(os.environ['GMAIL_USER'], os.environ['GMAIL_PASS'])

	# sendmail function takes 3 arguments: sender's address, recipient's address
	# and message to send - here it is sent as one string.
	print s.sendmail(me, address, msg.as_string())
	s.quit()

#send_id_email('joseph_engelman@brown.edu', 'your-client-id-here')