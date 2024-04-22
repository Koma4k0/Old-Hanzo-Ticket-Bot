import discord
import asyncio
import json
import sqlite3
import datetime
import chat_exporter
import io
from discord.interactions import Interaction
from vars import *
from discord.ext import commands

class AssignButton(discord.ui.View):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(timeout=None)

    @discord.ui.button(label=f"Assign", style = discord.ButtonStyle.green, custom_id="assign")
    async def Assign(self, interaction: discord.Interaction, button: discord.ui.Button,):
        conn = sqlite3.connect('user.db')
        cur = conn.cursor()

        cur.execute("SELECT * FROM ticket WHERE staff_id=? AND staff_id<>'NONE'", (interaction.user.id,))
        assigned_row = cur.fetchone()

        if assigned_row:
            await interaction.response.send_message("You are already assigned to a ticket.", ephemeral=True)
            conn.close()
            return

        cur.execute("SELECT * FROM ticket WHERE staff_id='NONE'")
        unassigned_tickets = cur.fetchall()

        for row in unassigned_tickets:
            channel_id = row[3]
            channel = interaction.guild.get_channel(channel_id)
            if channel:
                channel_category = channel.category
                if channel_category and channel_category.id != keyreset_category and channel_category.id != media_category:
                    channel = interaction.guild.get_channel(row[3])
                            
                    user_permission = discord.PermissionOverwrite(
                        view_channel=True,
                        send_messages=True,
                        attach_files=True,
                        embed_links=True,
                    )

                    existing_overwrites = channel.overwrites
                    existing_overwrites[interaction.user] = user_permission
                    await channel.edit(overwrites=existing_overwrites)
                    staffembed = discord.Embed(
                        title=f"{emoji_hanzo} Hanzo | Staff Assigned {emoji_hanzo}",
                        description=(
                            f"{interaction.user.mention} ***has been assigned to this ticket*** ({channel.mention})!\n"
                        ),
                        color=default_color
                    )
                    await channel.send(embed=staffembed)
                    await channel.send(f"<@{row[2]}>")

                    embed = discord.Embed(
                        title=f"{emoji_hanzo} Hanzo | Assigned {emoji_hanzo}",
                        description=(
                            "You have been assigned to a ticket!\n\n"
                            f"**See here:** {channel.mention}"
                        ),
                        color=default_color
                    )

                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    cur.execute("UPDATE ticket SET staff_id=? WHERE id=?", (interaction.user.id, row[0]))
                    conn.commit()
                    conn.close()
                    break
        await interaction.response.send_message("All tickets have a staffer assigned.", ephemeral=True)
        conn.close()
