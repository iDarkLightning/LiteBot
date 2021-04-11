from mongoengine import Document, StringField, ListField

class PollPreset(Document):
    """
    A schema modelling a poll preset document within the database.
    This schema is used for the poll command, in order to save and reuse various presets.
    name: The name of the preset, must be unique
    prompt: The question being asked for the prompt
    options: A list of all the options available for the poll
    """
    name = StringField(required=True, unique=True)
    prompt = StringField(required=True)
    options = ListField(StringField(), required=True, max_length=26)