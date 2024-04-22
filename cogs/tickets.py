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
from cogs.Buttons.Buttons import *
from cogs.Modals.modals import *
from cogs.Selectables.Cheats import *

class TicketPanelClass(discord.ui.View):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(timeout=None)

    @discord.ui.select(
        custom_id="support",
        placeholder="Choose a category",
        options=[
            discord.SelectOption(
                label="Purchase",
                emoji=emoji_key,
                value="Purchase"
            ),
            discord.SelectOption(
                label="Support",
                emoji=emoji_support2,
                value="Support"
            ),
            discord.SelectOption(
                label="Media",
                emoji=emoji_youtube,
                value="Media"
            ),
            discord.SelectOption(
                label="Key Reset",
                emoji=emoji_fire,
                value="KeyReset"
            )
        ]
    )
    async def callback(self, interaction, select):
        
        embed = discord.Embed(
            title=f"{emoji_hanzo} **Ticket Panel | Hanzo** {emoji_hanzo}",
            description=f"{emoji_info} **__How Do I Purchase?__**\n"
            f"Simply press the button below and choose the option that fits your needs!\n\n"
            f"{emoji_key} **__Instant Delivery__**\n"
            f"If you have Card or Crypto feel free to purchase directly from our website\n\n"
            f"{emoji_website} **__Website:__**\n"
            f"https://hanzo.cheating.store/\n\n"
            f"{emoji_money2} **__Payment Methods Accepted__**\n"
            f"{emoji_paypal} Paypal\n{emoji_cashapp} CashApp\n{emoji_venmo} Venmo\n{emoji_card} Card\n{emoji_crypto} Crypto (BTC, LTC, ETH)\n{emoji_binance} Binance Giftcards",
            color=default_color,
        )
        embed.set_image(url="https://media.discordapp.net/attachments/1126129988828147794/1195797810990293123/support.png?ex=65b54c7e&is=65a2d77e&hm=f27caee277f5e11f050b79a48dec1823576f27bd006f57a44e6b27abbd6ba1ed&format=webp&quality=lossless&width=1196&height=676&")
        await interaction.message.edit(embed=embed, view=TicketPanelClass(bot=self.bot))
        with sqlite3.connect('user.db') as conn:
            cur = conn.cursor()
            member_id = interaction.user.id
            cur.execute("SELECT discord_id FROM ticket WHERE discord_id=?", (member_id,))
            conn.commit()
            existing_ticket = cur.fetchone()
            if existing_ticket is None:                
                guild = self.bot.get_guild(guild_id)
                member_name = interaction.user.name
                staff_role = guild.get_role(staff_team_id)
                if "Purchase" in interaction.data['values']: 
                    if interaction.channel.id == ticket_channel_id:
                        ticket_name = member_name
                        category = self.bot.get_channel(purchase_category)
                        
                        overwrites = {
                            interaction.guild.default_role: discord.PermissionOverwrite(view_channel = False),
                            interaction.user: discord.PermissionOverwrite(view_channel = True, send_messages = True, attach_files = True, embed_links = True),
                        }

                        if category and len(category.channels) >= 50:
                            ticket_channel = await guild.create_text_channel(name=f"purchase-{ticket_name}",  topic=f"Purchase | {interaction.user.id}", overwrites=overwrites)
                        else:
                            ticket_channel = await guild.create_text_channel(name=f"purchase-{ticket_name}", category=category, topic=f"Purchase | {interaction.user.id}", overwrites=overwrites)

                        embed = discord.Embed(
                            title=f"{emoji_hanzo} Hanzo | Ticket {emoji_hanzo}",
                            description=(
                                "Your ticket has been successfully created!\n\n"
                                f"**See here:** {ticket_channel.mention}"
                            ),
                            color=default_color
                        )
                        await interaction.response.send_message(embed=embed, ephemeral=True)

                        embedPurchase = discord.Embed(
                            title=f"{emoji_money2} Purchase {emoji_money2}",
                            description=(
                                f"*Hello* {interaction.user.mention},\n"
                                f"*__Please explain what you need as much as possible.__*\n\nClick the button above to close this ticket"
                            ),
                            color=default_color
                        )

                        embedCheats = discord.Embed(
                            title=f"{emoji_money2} Purchase {emoji_money2}",
                            description=(
                                f"Follow the instructions to continue with your ticket. \n\n{emoji_info} Choose Product {emoji_info}\nClick below to choose the product you wish to purchase"
                            ),
                            color=default_color
                        )

                        await ticket_channel.send(embed=embedPurchase, view=CloseButton(self.bot))
                        await ticket_channel.send(embed=embedCheats, view=Cheats(self.bot))
                if "Media" in interaction.data['values']:
                    if interaction.channel.id == ticket_channel_id:
                        ticket_name = member_name
                        category = self.bot.get_channel(media_category)

                        overwrites = {
                            interaction.guild.default_role: discord.PermissionOverwrite(view_channel = False),
                            interaction.user: discord.PermissionOverwrite(view_channel = True, send_messages = True, attach_files = True, embed_links = True),
                        }

                        if category and len(category.channels) >= 50:
                            ticket_channel = await guild.create_text_channel(name=f"media-{ticket_name}",  topic=f"Media | {interaction.user.id}", overwrites=overwrites)
                        else:
                            ticket_channel = await guild.create_text_channel(name=f"media-{ticket_name}", category=category, topic=f"Media | {interaction.user.id}", overwrites=overwrites)


                        embed = discord.Embed(
                            title=f"{emoji_youtube} **Media Request** {emoji_youtube}",
                            description=(
                                f"Greetings {interaction.user.mention},\n\n"
                                "We appreciate your interest in our offerings. To explore a potential sponsorship collaboration, we kindly request the following details:\n\n"
                                "- Provide a concise overview of your platform or community.\n"
                                "- Highlight the central focus or theme of your platform.\n"
                                "- Share insights on how our products could enhance your audience's experience.\n"
                                "- Outline the scope and methods of your promotional outreach.\n"
                                "- Specify the exact number of complimentary keys you are seeking in exchange for sponsorship."
                            ),
                            color=default_color
                        )
                        await ticket_channel.send(embed=embed)

                        embed = discord.Embed(
                            title=f"{emoji_youtube} Media Info {emoji_youtube}",
                            description=(
                                f"Platform: ```NONE```\nName/Link: ```NONE```"
                            ),
                            color=default_color
                        )
                        messageInfo = await ticket_channel.send(embed=embed, view=CloseButton(bot=self.bot))

                        ticket_mention = ticket_channel.mention
                        process_gui = MediaModal(ticket_mention=ticket_mention, message=messageInfo, bot=self.bot)
                        await interaction.response.send_modal(process_gui)
                if "Support" in interaction.data['values']:
                    if interaction.channel.id == ticket_channel_id:
                        ticket_name = member_name
                        category = self.bot.get_channel(support_category)

                        overwrites = {
                            interaction.guild.default_role: discord.PermissionOverwrite(view_channel = False),
                            interaction.user: discord.PermissionOverwrite(view_channel = True, send_messages = True, attach_files = True, embed_links = True),
                        }

                        if category and len(category.channels) >= 50:
                            ticket_channel = await guild.create_text_channel(name=f"support-{ticket_name}",  topic=f"Support | {interaction.user.id}", overwrites=overwrites)
                        else:
                            ticket_channel = await guild.create_text_channel(name=f"support-{ticket_name}", category=category, topic=f"Support | {interaction.user.id}", overwrites=overwrites)


                        embed = discord.Embed(
                            title=f"{emoji_support} Support {emoji_support}",
                            description=(
                                f"Hello {interaction.user.mention},\n\n"
                                "**We're ready to assist you.** \n*Kindly furnish us with comprehensive details about the issue you're encountering, enabling us to offer effective support.*"
                            ),
                            color=default_color
                        )
                        await ticket_channel.send(embed=embed)

                        embed = discord.Embed(
                            title=f"{emoji_support} Issue Info {emoji_support}",
                            description=(
                                f"Product: ```NONE```\nIssue: ```NONE```"
                            ),
                            color=default_color
                        )

                        message2Send = await ticket_channel.send(embed=embed, view=CloseButton(bot=self.bot))
                        ticket_mention = ticket_channel.mention
                        process_gui = SupportModal(ticket_mention=ticket_mention, message=message2Send, bot=self.bot)
                        await interaction.response.send_modal(process_gui)
                if "KeyReset" in interaction.data['values']:
                    if interaction.channel.id == ticket_channel_id:
                        ticket_name = member_name
                        category = self.bot.get_channel(keyreset_category)

                        overwrites = {
                            interaction.guild.default_role: discord.PermissionOverwrite(view_channel = False),
                            interaction.user: discord.PermissionOverwrite(view_channel = True, send_messages = True, attach_files = True, embed_links = True),
                        }

                        if category and len(category.channels) >= 50:
                            ticket_channel = await guild.create_text_channel(name=f"reset-{ticket_name}",  topic=f"Reset | {interaction.user.id}", overwrites=overwrites)
                        else:
                            ticket_channel = await guild.create_text_channel(name=f"reset-{ticket_name}", category=category, topic=f"Reset | {interaction.user.id}", overwrites=overwrites)


                        embed = discord.Embed(
                            title=f"{emoji_key} Key Reset {emoji_key}",
                            description=(
                                f"Hello {interaction.user.mention},\n\n"
                                "**We're ready to assist you.** \n*Send your key and tell us the reason why we should do the HWID reset.*"
                            ),
                            color=default_color
                        )
                        await ticket_channel.send(embed=embed)

                        embed = discord.Embed(
                            title=f"{emoji_key} Key Reset {emoji_key}",
                            description=(
                                f"Key: ```NONE```\nReason: ```NONE```"
                            ),
                            color=default_color
                        )

                        message2Send = await ticket_channel.send(embed=embed, view=CloseButton(bot=self.bot))
                        ticket_mention = ticket_channel.mention
                        process_gui = KeyResetModal(ticket_mention=ticket_mention, message=message2Send, bot=self.bot)
                        await interaction.response.send_modal(process_gui)    
                cur.execute("INSERT INTO ticket (discord_name, discord_id, channel_id, staff_id) VALUES (?, ?, ?, ?)", (member_name, member_id, ticket_channel.id, "NONE"))
                cur.execute("SELECT id, discord_name FROM ticket WHERE discord_id=?", (member_id,))                    
                conn.commit()
            else:
                embed = discord.Embed(
                    title=f"{emoji_hanzo} Hanzo | Error {emoji_hanzo}",
                    description = (
                        f"**__You have an open ticket with us.__** \n\n"
                        "*If it's a bug or you face issues, contact our staff team via DM, providing this error message for assistance.*"
                    ),
                    color=default_color
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
        conn.close()
        return

