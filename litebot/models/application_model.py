from mongoengine import Document, StringField, IntField, DictField, ListField

class Application(Document):
    """
    A schema modelling a user's application.
    Used by the application module.
    `name` The name of the applicant
    `confirmation_message` The message that was used to verify the applicant's creation
    `application_embeds` The embeds for the application
    `ticket_id` The ID for the created ticket channel
    """
    name = StringField()
    confirmation_message = IntField(required=True, unique=True)
    application_embeds = ListField(DictField(), required=True)
    ticket_id = IntField()