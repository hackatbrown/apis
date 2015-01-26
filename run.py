from api import app
from os import environ

if __name__ == '__main__':
    port = int(environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)