from mongoengine import Document, StringField, IntField

class TrackedEvent(Document):
    """
    A schema modelling a tracked event document in the database.
    A tracked event is a certain discord model that is currently being tracked for some purpose.
    tracking_id: The ID of the model that is being tracked. Must be unique
    event_tag: The tag, essentially the type of the event being tracked. Options: (poll)
    """
    tracking_id = IntField(required=True, unique=True)
    event_tag = StringField(required=True, choices=("poll",))