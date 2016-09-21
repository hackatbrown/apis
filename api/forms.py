from flask_wtf import Form
from wtforms import StringField, TextAreaField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Email
from api.scripts.add_client import add_client_id
from api.scripts.email_handler import send_id_email
from api.scripts.add_documentation import add_documentation
from api.scripts.add_member import add_member


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


class DocumentationForm(Form):
    name = StringField('Name', validators=[DataRequired()])
    urlname = StringField('URL Name', validators=[DataRequired()])
    imageurl = StringField('Image URL', validators=[DataRequired()])
    contents = TextAreaField('Contents', validators=[DataRequired()])

    def validate(self):
        if Form.validate(self):
            documentation = add_documentation(self.contents.data,
                                              self.name.data, self.urlname.data, self.imageurl.data)
            if documentation:
                return True
            else:
                self.name.errors.append("Client ID could not be created.")
                return False
        else:
            return False


class MemberForm(Form):
    name = StringField('Name', validators=[DataRequired()])
    imageurl = StringField('Image URL', validators=[DataRequired()])
    about = TextAreaField('Contents', validators=[DataRequired()])

    def validate(self):
        if Form.validate(self):
            member = add_member(self.about.data,
                                self.name.data, self.imageurl.data)
            if member:
                return True
            else:
                self.name.errors.append("Member could not be created.")
                return False
        else:
            return False
