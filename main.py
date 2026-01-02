import discord
import os
import asyncio
import logging
from discord.ext import commands
from dotenv import load_dotenv
from economy_db import DatabaseManager 
import json

# Setup Logging
logging.basicConfig(level=logging.INFO)

# Load Environment and Config
load_dotenv()
with open("config.json", "r") as f:
    CONFIG = json.load(f)

TOKEN = os.getenv("DISCORD_TOKEN")

# Bot Setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
guildobj = discord.Object(id=679982379670175755)

async def load_extensions():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")
            
@bot.event
async def on_ready():    
    try:
        bot.tree.copy_global_to(guild=guildobj)
        synced = await bot.tree.sync(guild=guildobj)
        logging.info(f"Synced {len(synced)} command(s).")
    except Exception as e:
        logging.error(f"Failed to sync commands: {e}")

async def main():
    if not TOKEN:
        print("Error: DISCORD_TOKEN not found.")
        return

    # 1. Initialize the Database Manager
    db = DatabaseManager(CONFIG["database_name"])
    
    # 2. Connect BEFORE starting the bot
    await db.connect()
    await db.initialize()
    
    # 3. Attach db to the bot so Cogs can access it via self.bot.db
    bot.db = db
    logging.info("Database connected and attached to bot.")

    try:
        async with bot:
            await load_extensions()
            await bot.start(TOKEN)
    except KeyboardInterrupt:
        # This block catches Ctrl+C
        logging.info("Shutdown signal received.")
    finally:
        # 4. ALWAYS close the DB, even if the bot crashes
        logging.info("Closing database connection...")
        await db.close()
        logging.info("Database closed. Goodbye!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # Handle the extra error output usually caused by Ctrl+C on Windows/Linux
        pass