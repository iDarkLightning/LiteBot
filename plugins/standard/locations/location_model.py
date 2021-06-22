from mongoengine import Document, StringField, ListField, IntField

class Location(Document):
    location_id = StringField(required=True, unique=True)
    name = StringField(required=True, unique=True)
    dimension = StringField(required=True)
    coordinates = ListField(IntField(), max_length=3)
    tolerance = IntField(max_value=1000)

