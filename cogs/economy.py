import discord
from discord import app_commands
from discord.ext import commands
import random
import json
import logging

# Load config
with open("config.json", "r") as f:
    CONFIG = json.load(f)

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.symbol = CONFIG["currency_symbol"]

    async def _ensure_user_exists(self, user_id: int):
        """Helper to check if user exists, if not, creates them."""
        balance = await self.bot.db.get_balance(user_id)
        if balance is None:
            await self.bot.db.create_account(user_id, CONFIG["starting_balance"])
            return True
        return False

    @app_commands.command(name="balance", description="Check your current wallet balance")
    async def check_balance(self, interaction: discord.Interaction):
        await self._ensure_user_exists(interaction.user.id)
        balance = await self.bot.db.get_balance(interaction.user.id)
        
        embed = discord.Embed(
            title=f"💰 {interaction.user.display_name}'s Balance", 
            color=discord.Color.gold()
        )
        embed.add_field(name="Wallet", value=f"{balance} {self.symbol}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="work", description="Do some work to earn currency")
    # NEW COOLDOWN: 1 use per 'work_cooldown_seconds' per User
    @app_commands.checks.cooldown(1, float(CONFIG["work_cooldown_seconds"]), key=lambda i: (i.user.id))
    async def work(self, interaction: discord.Interaction):
        await self._ensure_user_exists(interaction.user.id)
        
        earnings = random.randint(CONFIG["work_min_earnings"], CONFIG["work_max_earnings"])
        await self.bot.db.update_balance(interaction.user.id, earnings)
        
        await interaction.response.send_message(
            f"🔨 You worked hard and earned **{earnings} {self.symbol}**!"
        )

    @app_commands.command(name="give", description="Transfer currency to another user")
    @app_commands.describe(recipient="The user to send money to", amount="Amount to send")
    async def transfer(self, interaction: discord.Interaction, recipient: discord.Member, amount: int):
        if amount <= 0:
            return await interaction.response.send_message("You can't send negative amounts!", ephemeral=True)
        if recipient.bot:
            return await interaction.response.send_message("You can't send money to bots.", ephemeral=True)
        if recipient.id == interaction.user.id:
            return await interaction.response.send_message("You can't send money to yourself!", ephemeral=True)

        await self._ensure_user_exists(interaction.user.id)
        await self._ensure_user_exists(recipient.id)

        sender_bal = await self.bot.db.get_balance(interaction.user.id)

        if sender_bal < amount:
            return await interaction.response.send_message(
                f"❌ Insufficient funds! You only have {sender_bal} {self.symbol}.", ephemeral=True
            )

        # Perform transaction
        await self.bot.db.update_balance(interaction.user.id, -amount)
        await self.bot.db.update_balance(recipient.id, amount)

        await interaction.response.send_message(
            f"💸 Successfully transferred **{amount} {self.symbol}** to {recipient.display_name}!"
        )

    # --- Error Handler for Cooldowns ---
    @work.error
    async def on_work_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            # Calculate remaining time
            minutes, seconds = divmod(int(error.retry_after), 60)
            msg = f"⏳ You're tired! Try again in **{minutes}m {seconds}s**."
            await interaction.response.send_message(msg, ephemeral=True)
        else:
            logging.error(f"Error in work command: {error}")

async def setup(bot):
    await bot.add_cog(Economy(bot))