from flask_wtf import Form
from wtforms import StringField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Email
from api.scripts.add_client import add_client_id
from api.scripts.email_handler import send_id_email

class SignupForm(Form):
    name = StringField('Name', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    
    def validate(self):
        if Form.validate(self): 
            client_id = add_client_id(self.email.data, self.name.data)
            if client_id:
                send_id_email(self.email.data, self.name.data, client_id)
                return True
            else:
                self.email.errors.append("Client ID could not be created. Is your email correct?")
                return False
        else:
            return False

