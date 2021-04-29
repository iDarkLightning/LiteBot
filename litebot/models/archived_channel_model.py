from mongoengine import Document, IntField, StringField, DictField, ListField


class ArchivedChannel(Document):
    archiver = DictField(required=True)
    pins = ListField(DictField(), required=True)
    channel_id = IntField(required=True, unique=True)
    name = StringField(required=True)
    topic = StringField()
    category = StringField()
    messages = ListField(DictField(), required=True)
    users = ListField(DictField(), required=True)