# Modules
Modules are used to add custom exentions and commands that are not related to minecraft. The current available modules are:

* `applications`: Creates an application system that links to a google form and creates a ticket automatically upon receiving
a new submission in the google form.
* `discor_utils`: Adds various discord utils, such as a `clear` command, `auto_role`, and `scalable_voice`
* `games`: Will contain all the games that the bot supports, currently only adds the hangman game

## Add your own module
Modules are a great way to implement features of our own within the bot. The steps to do so are found below:

First create this hierarchy within the `modules` directory:

```
modules/<module_name>
/__init__.py
/Cog.py
``` 

Your `__init__` must contain two functions `setup` and `config`, as shown below.

```python
def setup(bot):
    bot.load_cog('<module_name>', commands.Cog)

def config():
    return {'a': 'b'}
```

We use a custom `load_cog` method instead of the standard `add_cog` in order to properly write the config. The first argument
will be the module name, and the second will be an instance of `commands.Cog`. The config function is used to write the config
required for your module. If your module does not require a config, you can simply return `None` instead of a `dict`

*Please note that any errors you may face whilst writing your own module is completely on you. If you follow all the instructions
properly, this should not be an issue*
## Contribute
Feel free to make a pull request if you feel your module would be a good addition to the bot!