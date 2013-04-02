from flask.ext.wtf import Form, TextField, validators

class RoomForm(Form):
    name = TextField('Name', [validators.Required()])
