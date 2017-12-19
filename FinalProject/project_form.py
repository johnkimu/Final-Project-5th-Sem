from wtforms import Form, TextAreaField, validators, StringField

class ProjectForm(Form):
    tittle = StringField('Tittle', [validators.length(min=1, max=200)])
    body = TextAreaField('Body', [validators.length(min=30)])


