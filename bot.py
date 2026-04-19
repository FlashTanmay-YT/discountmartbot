import discord
from discord import app_commands
from discord.ext import commands
import os

# Replace 'YOUR_BOT_TOKEN' with your actual bot token from Discord Developer Portal
TOKEN = os.getenv('TOKEN')


OWNER_ID = 773101810818744330

DEVELOPER_ID = OWNER_ID

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True  # Needed for reading message content
intents.members = True  # Needed for UserConverter to work properly in guilds
bot = commands.Bot(command_prefix='+', intents=intents)


stocks = {
    'MCFA': {'name': 'MCFA', 'stock': 10},
    'DonutSMP $$': {'name': 'DonutSMP $$', 'stock': 5},
    'Steam Games': {'name': 'Steam Games', 'stock': 20},
    'Discord Decorations': {'name': 'Discord Decorations', 'stock': 15},
    'Nitro': {'name': 'Nitro', 'stock': 8}
}

@bot.event
async def on_ready():
    print(f'Bot {bot.user} is ready and connected to Discord!')
    await bot.tree.sync()  

# Slash command for /stock
@bot.tree.command(name="stock", description="Check all stock levels")
async def stock(interaction):
    embed = discord.Embed(
        title="DISCOUNT MART Inventory",
        description="Here are the current stock levels for all categories:",
        color=discord.Color.blue()
    )
    
    for category, data in stocks.items():
        embed.add_field(
            name=data['name'],
            value=f"Stock: {data['stock']}",
            inline=True
        )
    
    await interaction.response.send_message(embed=embed)

# Slash command for /update_stock <category> <new_stock> (Owner only)
@bot.tree.command(name="update_stock", description="Update stock for a category (Owner only)")
@app_commands.describe(category="Choose a category", new_stock="New stock amount")
@app_commands.choices(category=[
    app_commands.Choice(name="MCFA", value="MCFA"),
    app_commands.Choice(name="DonutSMP $$", value="DonutSMP $$"),
    app_commands.Choice(name="Steam Games", value="Steam Games"),
    app_commands.Choice(name="Discord Decorations", value="Discord Decorations"),
    app_commands.Choice(name="Nitro", value="Nitro")
])
async def update_stock(interaction, category: str, new_stock: int):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("You are not authorized to use this command.")
        return
    
    category = category.lower()  # Make it case-insensitive
    if category in [key.lower() for key in stocks.keys()]:
        # Find the matching key (case-insensitive)
        for key in stocks:
            if key.lower() == category:
                stocks[key]['stock'] = new_stock
                await interaction.response.send_message(f"Stock for {stocks[key]['name']} updated to {new_stock}.")
                return
    else:
        await interaction.response.send_message("Invalid category. Available categories: MCFA, DonutSMP $$, Steam Games, Discord Decorations, Nitro")


# /cmd for server info
@bot.tree.command(name="server_info", description="Get information about the server")
async def server_info_slash(interaction):
    guild = interaction.guild
    embed = discord.Embed(
        title=f"{guild.name} Server Info",
        color=discord.Color.green()
    )
    embed.add_field(name="Owner", value=guild.owner.mention, inline=True)
    embed.add_field(name="Members", value=guild.member_count, inline=True)
    embed.add_field(name="Created at", value=guild.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
    embed.add_field(name="Channels", value=len(guild.channels), inline=True)
    embed.add_field(name="Roles", value=len(guild.roles), inline=True)
    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
    await interaction.response.send_message(embed=embed)

# prefix cmd for srv info
@bot.command(name="server_info")
async def server_info_prefix(ctx):
    guild = ctx.guild
    embed = discord.Embed(
        title=f"{guild.name} Server Info",
        color=discord.Color.green()
    )
    embed.add_field(name="Owner", value=guild.owner.mention, inline=True)
    embed.add_field(name="Members", value=guild.member_count, inline=True)
    embed.add_field(name="Created At", value=guild.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
    embed.add_field(name="Channels", value=len(guild.channels), inline=True)
    embed.add_field(name="Roles", value=len(guild.roles), inline=True)
    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
    await ctx.send(embed=embed)

# /cmd for bot info
@bot.tree.command(name="bot_info", description="Get information about the bot")
async def bot_info_slash(interaction):
    embed = discord.Embed(
        title="Bot Info",
        description="Information about Discount Mart Bot",
        color=discord.Color.purple()
    )
    embed.add_field(name="Name", value=bot.user.name, inline=True)
    embed.add_field(name="ID", value=bot.user.id, inline=True)
    embed.add_field(name="Created at", value=bot.user.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
    embed.add_field(name="Users", value=sum(guild.member_count for guild in bot.guilds), inline=True)
    embed.add_field(name="Developer", value=f"<@{DEVELOPER_ID}>", inline=True)
    embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else None)
    await interaction.response.send_message(embed=embed)
    
# Message autoresponder (example: responds to "hello" or mentions of the store)
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return  # Ignore bot's own messages

    content = message.content.lower()

    # Skip autoresponders for command messages (starting with '+')
    if not message.content.startswith('+'):
        # Autoresponder for bot mentions: reply with help message
        if bot.user in message.mentions:
            await message.channel.send("Need help? Use /stock to check inventory. For purchases, create a ticket. Available categories: MCFA, DonutSMP $$, Steam Games, Discord Decorations, Nitro.")
            return  # Stop further processing to avoid multiple responses

        # Autoresponder for "hello" or "discount mart"
        if 'new here' in content or 'what to do here' in content:
            await message.channel.send("Hello! Welcome to DISCOUNT MART! We sell games and game accounts. Use /stock to check our inventory!")
            return

        # Autoresponder for "payment methods"
        if 'payment methods' in content or 'payment method' in content:
            await message.channel.send("We accept payments via UPI ID. Please create a ticket for purchase details!")
            return
        
        # Autoresponder for "help"
        if 'help' in content:
            await message.channel.send("Need help? Use /stock to check inventory. For purchases, create a ticket. Available categories: MCFA, DonutSMP $$, Steam Games, Discord Decorations, Nitro.")
            return

    # Process other commands (important for slash commands to work)
    await bot.process_commands(message)

# Run the bot
bot.run("")
