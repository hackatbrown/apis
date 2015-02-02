from sys import argv

from api import db, meta

if __name__ == '__main__':
	if len(argv) != 2:
		print "Usage: python -m api.scripts.enable_client <client_id>"
	else:
		print meta.validate_client(argv[1])