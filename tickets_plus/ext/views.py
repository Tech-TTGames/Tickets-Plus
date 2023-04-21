"""Generic discord.py views for tickets_plus.

Those are various buttons and select menus used throughout the bot.
Note that these are not cogs, but rather discord.py views.

Typical usage example:
    ```py
    from tickets_plus.ext import views

    @bot.command()
    async def example(ctx):
        await ctx.send("Example", view=views.ExampleView())
        ...
    ```
"""
# License: EPL-2.0
# SPDX-License-Identifier: EPL-2.0
# Copyright (c) 2021-present The Tickets+ Contributors
# This Source Code may also be made available under the following
# Secondary Licenses when the conditions for such availability set forth
# in the Eclipse Public License, v. 2.0 are satisfied: GPL-3.0-only OR
# If later approved by the Initial Contrubotor, GPL-3.0-or-later.

import discord


class Confirm(discord.ui.View):
    """A confirmation button set.

    Allows the user to confirm or cancel an action.

    Attributes:
        value: Whether the user confirmed or not.
            `None` if the user didn't confirm or cancel.
            `bool` if the user confirmed or canceled.
    """

    value: bool | None

    def __init__(self):
        """Initialises the view.

        We prep the button and set return value to None.
        """
        super().__init__()
        self.value = None

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction,
                      button: discord.ui.Button):
        """The confirm button was pressed.

        We set the return value to True, disable the button and stop the view.

        Args:
            interaction: The interaction that triggered the button.
            button: The button that was pressed.
        """
        await interaction.response.send_message("Confirmed", ephemeral=True)
        self.value = True
        button.disabled = True
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction,
                     button: discord.ui.Button):
        """The cancel button.

        We set the return value to False, disable the button and stop the view.

        Args:
            interaction: The interaction that triggered the button.
            button: The button that was pressed.
        """
        await interaction.response.send_message("Cancelled", ephemeral=True)
        self.value = False
        button.disabled = True
        self.stop()
