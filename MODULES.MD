# Modules
Modules are used to add custom exentions and commands that are not related to minecraft. The current available modules are:

* `applications`: Creates an application system that links to a google form and creates a ticket automatically upon receiving
a new submission in the google form.
* `discord_utils`: Adds various discord utils, such as a `clear` command, `auto_role`, `list` command and `scalable_voice`
* `games`: Will contain all the games that the bot supports, currently only adds the hangman game
*  `backups` Server backups for minecraft (requires to be running on same computer)
* `quotes` Save notable quotes

## Add your own module
Modules are a great way to implement features of our own within the bot. The steps to do so are found below:

First create this hierarchy within the `modules` directory:

```
modules/<module_name>
/__init__.py
/Cog.py
``` 

Your `__init__` must contain a function `setup`, and can contain a `config` property as well as a `requirements` function,
which must return a boolean value.

```python
def setup(bot):
    bot.add_cog(commands.Cog)

def requirements(bot):
    return 1 > 0

def config(bot):
    return {"a": "a"}

```

*Please note that any errors you may face whilst writing your own module is completely on you. If you follow all the instructions
properly, this should not be an issue*
## Contribute
Feel free to make a pull request if you feel your module would be a good addition to the bot!
