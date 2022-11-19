'''
Declare variables used in bot.
This file is a based on the variables.py file from my other bot.
'''
import json
from string import Template
from typing import List, Union, Literal
from logging.handlers import RotatingFileHandler

import discord
from discord.ext import commands

#v[major].[minor].[release].[build]
VERSION = "v0.0.2.1-DEV"


intents = discord.Intents.default()
handler = RotatingFileHandler(filename='discord.log',
                            encoding='utf-8',
                            mode='w',
                            backupCount=10,
                            maxBytes=100000)

class Secret:
    '''Class for secret.json management'''
    def __init__(self) -> None:
        self._file = 'secret.json'
        with open(self._file,encoding="utf-8",mode='r') as secret_f:
            self.secret = json.load(secret_f)
        self.token = self.secret['token']

    def __repr__(self) -> str:
        return "[OBFUSCATED]"

    def __str__(self) -> str:
        return "[OBFUSCATED]"



class Config: #Note: Currently config is global, but I plan to make it per server.
    '''Class for convinient config access'''
    def __init__(self,bot: Union[commands.Bot,Literal["offline"]]) -> None:
        self._file = 'config.json'
        with open(self._file,encoding="utf-8",mode='r') as config_f:
            self._config: dict = json.load(config_f)
        self._bot = bot

    def __dict__(self) -> dict:
        return self._config

    def update(self) -> None:
        '''Update the config.json file to reflect changes'''
        with open(self._file,encoding="utf-8",mode='w') as config_f:
            json.dump(self._config,config_f,indent=4)
            config_f.truncate()

    @property
    def guild(self) -> discord.Guild:
        '''Returns the guild object'''
        if isinstance(self._bot,str):
            raise ValueError("Use online config.")
        gld = self._bot.get_guild(self._config['guild_id'])
        if isinstance(gld, discord.Guild):
            return gld
        raise ValueError("Guild Not Found")

    @guild.setter
    def guild(self, value: discord.Guild) -> None:
        '''Sets the guild object'''
        self._config['guild_id'] = value.id
        self.update()

    @property
    def ticket_users(self) -> List[int]:
        '''List of users who are tracked for ticket creation'''
        return self._config.get('ticket_users', [508391840525975553])

    @ticket_users.setter
    def ticket_users(self, value: List[int]) -> None:
        '''Sets the list of users who are tracked for ticket creation'''
        self._config['ticket_users'] = value
        self.update()

    @property
    def staff(self) -> List[discord.Role]:
        '''List of users who are staff'''
        staff = []
        for role in self._config.get('staff',[]):
            stf_role = self.guild.get_role(role)
            if isinstance(stf_role, discord.Role):
                staff.append(stf_role)
        return staff

    @property
    def staff_ids(self) -> List[int]:
        '''List of user ids who are staff'''
        return self._config.get('staff',[])

    @staff.setter
    def staff(self, value: List[discord.Role]) -> None:
        '''Sets the list of users who are staff'''
        self._config['staff'] = [role.id for role in value]
        self.update()

    @property
    def staff_ping(self) -> bool:
        '''Returns if staff should be pinged on ticket creation'''
        return self._config.get('staff_ping', True)

    @staff_ping.setter
    def staff_ping(self, value: bool) -> None:
        '''Sets if staff should be pinged on ticket creation'''
        self._config['staff_ping'] = value
        self.update()

    @property
    def open_msg(self) -> Template:
        '''Returns the message sent when a ticket is opened'''
        return Template(self._config.get('open_msg', "Staff notes for Ticket $channel."))

    @open_msg.setter
    def open_msg(self, value: str) -> None:
        '''Sets the message sent when a ticket is opened'''
        self._config['open_msg'] = value
        self.update()

    @property
    def staff_team(self) -> str:
        '''Returns the staff team name'''
        return self._config.get('staff_team', "Staff Team")

    @staff_team.setter
    def staff_team(self, value: str) -> None:
        '''Sets the staff team name'''
        self._config['staff_team'] = value
        self.update()

    @property
    def msg_discovery(self) -> bool:
        '''Returns if messages should be discovered'''
        return self._config.get('msg_discovery', True)

    @msg_discovery.setter
    def msg_discovery(self, value: bool) -> None:
        '''Sets if messages should be discovered'''
        self._config['msg_discovery'] = value
        self.update()
