from mongoengine import Document, StringField, ListField

class PollPreset(Document):
    name = StringField(required=True, unique=True)
    prompt = StringField(required=True)
    options = ListField(StringField(), required=True, max_length=26)