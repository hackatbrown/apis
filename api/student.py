from api import app

'''
TODO: Look into using Active Directory / LDAP for authentication.

            Mongo Applications: http://docs.mongodb.org/manual/tutorial/configure-ldap-sasl-activedirectory/
            Brown's Active Dir: http://www.brown.edu/information-technology/services/active-directory

TODO: Establish this document model in the database / debate this model

db.student {
        'username' : str,            || the username of the user
        'password' : str,            || the password of the user
        'email' : str                || the email
        'last_login' : date,                || the date of the last login
        'login_attempts': int,                || the number of login attempts since the last succesfull login
                                                                        *If login attempts goes above 5, lock the account and automatically
                                                                         issue an email to the supplied email address

                                                                        *Possible Implementations:
                                                                         - Run a service every n- minutes to subtract one from the login_attempts
                                                                         - Consider an implementation where the client can only rerequest after a certain amount of time.
                                                                         - This would involve keeping the current time, the last failed login time, and the login penalty.

        'token' : str                    || the current valid login token
                                                                        *This is the user's key to the world
        'expiration' : date                     || the expiration date of the token. Help keep things fresh.
}
'''


@app.route('/student/login')
def login(L):
    '''Allows a user to receive a token in exchange for a valid password / username combination.'''
    # TODO: Implement login
    Dict = {}
    count = 0
    idnum = 1000000
    while len(L) != 0:
        Dict.append(L[count], idnum)
        count += 1
        idnum += 1
    return Dict


@app.route('/student/balance')
def balance():
    '''Allows a user to view their various balances.'''
    # TODO: Implement balance retrieval
    return


@app.route('/student/transactions')
def transactions():
    '''Allows a user to view their transaction history'''
    # TODO: Consider a time
