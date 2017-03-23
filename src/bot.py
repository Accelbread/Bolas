import discord
import logging
import asyncio

from .commands import CommandPlugin
from .chat_hooks import HookPlugin


class Bolas(discord.Client):

    def __init__(self, token):
        """ Constructor for the  bot class.

        Args:
            token (str): the token for the discord bot.
        """
        super().__init__()

        self.token = token
        self.commands = {}
        for command in CommandPlugin.plugins:
            # command.command is a string version of it, for example !ping
            self.commands[command.command] = command

        self.chat_hook = HookPlugin.plugins
        self.admins = []

        self.HELP_COMMAND = "!help"
        self.MESSAGE_MAX_LEN = 2000

        # Concatenate the docstrings from each one of the plugins
        self.docstring = "```{0}```".format("\n\n".join(
            x.__doc__.strip() for x in (CommandPlugin.plugins +
                                        HookPlugin.plugins))
        )

        self.logger = logging.getLogger("discord")
        handler = logging.FileHandler(
            filename='discord.log', encoding='utf-8', mode='w')
        handler.setFormatter(logging.Formatter(
            '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
        self.logger.addHandler(handler)

    def get_admins(self):
        """ A generator that yields all the administrators."""
        admin_permissions = ["administrator"]
        for server in self.servers:
            for member in server.members:
                for role in member.roles:
                    for permission in role.permissions:
                        # permissions are tuples
                        if (permission[0] in admin_permissions and
                                permission[1]):
                            yield member

    def is_admin(self, user):
        """ Checks if a user is an admin """
        return user in self.admins or user.id in self.get_admins()

    async def say(self, message, channel):
        """ Wrapper for send_typing and send_message """

        if (len(message) > self.MESSAGE_MAX_LEN):
            print("Splitting into two messages.")
            await self.say(message[:self.MESSAGE_MAX_LEN], channel)
            await self.say(message[self.MESSAGE_MAX_LEN:], channel)
            return

        print("Saying: {0}".format(message).encode("ascii", "ignore"))
        await self.send_typing(channel)
        await self.send_message(channel, message)

    async def on_message(self, message):
        """Overloaded Method"""
        if message.author != self.user:
            # Get the message itself.
            text = message.content
            user = message.author

            # Split it into words.
            msg = text.split(" ")

            # The first word is the command.
            command = msg[0]

            # The remainder are the arguments.
            args = msg[1:]

            print("{0} sent: {1} {2}".format(user, command, args).
                  encode("ascii", "ignore"))

            if (command == self.HELP_COMMAND):
                await self.say(self.docstring,
                               message.channel)
                return

            for name, cmd in self.commands.items():
                if (command == name):
                    await self.say(str(cmd.func(user, args)),
                                   message.channel)
                    # Don't run the chat hook if we found a command
                    return

            for plugin in self.chat_hook:
                result = plugin.func(text, message.server.id)
                if result:
                    await self.say(result, message.channel)

    async def on_ready(self):
        """Overloaded Method"""
        print("Logged in as {0}".format(self.user.name))

        await self.change_presence(game=discord.Game(
            name=": Add me to your server with the !addme command."))
