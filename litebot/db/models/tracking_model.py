from mongoengine import Document, StringField, IntField

class TrackedEvent(Document):
    tracking_id = IntField(required=True, unique=True)
    event_tag = StringField(required=True, choices=("poll",))