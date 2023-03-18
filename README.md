# Welcome to Tickets+

<img align="left" src="https://raw.githubusercontent.com/Tech-TTGames/Tickets-Plus/main/branding/rounded.png" height="200" width="200"/>

[![CodeQL](https://github.com/Tech-TTGames/Tickets-Plus/actions/workflows/codeql.yml/badge.svg?branch=main)](https://github.com/Tech-TTGames/Tickets-Plus/actions/workflows/codeql.yml) [![Pylint](https://github.com/Tech-TTGames/Tickets-Plus/actions/workflows/pylint.yml/badge.svg?branch=main)](https://github.com/Tech-TTGames/Tickets-Plus/actions/workflows/pylint.yml) [![DeepSource](https://deepsource.io/gh/Tech-TTGames/Tickets-Plus.svg/?label=active+issues&show_trend=true&token=ourUeg696DFMDcZDoZi0ZqGn)](https://deepsource.io/gh/Tech-TTGames/Tickets-Plus/?ref=repository-badge)

A Discord bot that adds extensions to the [Tickets](https://github.com/TicketsBot) discord bot.[^1]
Made by the Tickets+ team, a group of volunteers[^0] who want to add features to the Tickets bot. But didn't know rust.

With this bot you can add staff notes, staff responses, and community support to your server.
This bot acts as a supplimentary, seperate bot[^2] to the main Tickets bot.

## Feature 1 - Staff Notes

Private threads are *(now)* free!

This creates a private thread in a channel and adds the staff roles to it[^3].
You can now disable pings, just use /settings staffpings to toggle.
The 'open message' is adjustable via /settings openmsg. $channels is replaced with the channel mention.

## Feature 2 - Staff Response

You can now respond as the staff team[^3] using /respond.
The command is limited to users with roles added to staff[^3].
The 'name' of the team[^3] is adjustable via /settings staffname.

## Feature 3 - Community Support

Automatically adds roles[^4] to the channel created by Tickets bots[^5].
Additionally, facilitates correct ping behavior with said community roles.

### Minor Feature 1 - Message Discovery

The bot will display previews of discord message links.
Requires message content intent.

### Minor Feature 2 - Strip Buttons

Due to the main Tickets bot not facilitating permissions check withthe 'Close' and 'Close with Reason' buttons this bot will strip the buttons enabling the use of / command perms to limit access.
Toggle with /setting stripbuttons.

## Setup

Here are the steps to host your copy of [this bot.](https://github.com/Tech-TTGames/Tickets-Plus)[^6]:

1. Open the directory you want the project to be placed in.
2. Use `git clone https://github.com/Tech-TTGames/Tickets-Plus.git` or download and unpack [the repo](https://github.com/Tech-TTGames/Tickets-Plus/archive/refs/heads/main.zip).
3. Ensure that python3.11 is installed and available, same for pip.
4. Run `pip install poetry`.
    - Change some poetry settings as-needed. You can add the `--local` flag to set those settings only to the current directory
        + `poetry config virtualenvs.in-project true` installs the virtual environment in project not in a poetry-specific location (reccomended).
        + `poetry config virtualenvs.create false` if you don't want poetry to use a venv (not reccomended).
5. Run `poetry install`
    - Depending on DB used add `-E pgsql` or `-E sqlite`
    - If you want development packages add `--with dev`
6. Install PostgreSQL. [Guide Here](https://www.postgresql.org/download/)
    1. Set up automatic postgres startup [Linux](https://www.postgresql.org/docs/current/server-start.html) and for windows just start it via `services.msc`
    2. Set up user and database for bot. <FIELD> are required and to be repalced with your own stuff. [FIELD] are optional and can be ignored.
        - Linux:
            1. `sudo -u postgres -i`
            2. `createuser <dbuser> --pwprompt` The prompt will ask you for password for new user - <dbpass>
            3. `createdb <dbname> [comment] -E UTF8 -O <dbuser>` <dbuser> being the same as in previous step.
        - Windows:
            1. If the installed postgres bin isn't in PATH use `cd` to go to the instalaltion bin.
            2. `createuser <dbuser> --pwprompt -U postgres`. The prompt will ask you for password to postgres and password for new user - <dbpass>.
            3. `createdb <dbname> [comment] -E UTF8 -O <dbuser> -U postgres` <dbuser> being the same as in previous step.
    3. Fill out config.json based on the database config environment. (refer to example_config.json)
        - Don't change "dbtype" unless you're using sqlite.
        - Unless you are using remote server/changed config don't touch "dbhost" and "dbport".
        - Otherwise all parameters are named *here* and in example_config.json the same
5. Create the bot on [Discord Developers](https://discord.com/developers/applications).
    7.1. Create application however you want.
    7.2. Create a bot.
    7.3. Turn on the 'Message Content' privileged intent. Probably disable 'Public Bot'.
    7.4. Input your bot token to secret.json. (Refer to example_secret.json)
    7.5. Invite the bot to your server! Replace the <CLIENT_ID> in the below invites with numbers from https://discord.com/developers/applications/<CLIENT_ID>/
         - The ***easy link***:
            `https://discord.com/api/oauth2/authorize?client_id=<CLIENT_ID>&permissions=8&scope=bot%20applications.commands`
         - The *safer link*:
            `https://discord.com/api/oauth2/authorize?client_id=<CLIENT_ID>&permissions=535059492048&scope=bot%20applications.commands`
6. Start your bot! Use `poetry run start` or after activating venv (if present) `python3 
    - Probably add a background service that will restart the bot on boot. *I use systemctl for my bots.*

### Database Documentation

* [Database Documentation](https://tickets-plus.techttgames.dev/database_info.html)

[^1]: This bot is not affiliated with the TicketsBot team.  When a feature is added to the main bot any feature that is no longer needed will be discontinued here.
[^0]: [Tech-TTGames](https:\\github.com\Tech-TTGames), I'm the only one here right now. I had some help in general but I'm the only one who has done any coding. More people are welcome to join. I had help with organization and checking my code from [kk5dire](https://github.com/kk5dire) and [Ben Foster](https://github.com/benfoster04) with hosting and some documentation changes.
[^2]: This setup assumes you have the main bot added to the server and configured, Support will not be provided to those who do not assume a likewise configuraton.
[^3]: Staff role defined in per-server settings.
[^4]: Community roles defined in per-server settings.
[^5]: Tickets bot defined in per-server settings.
[^6]: Note that there is no publicly hosted instance of the bot at this time. One may be added in the future.
