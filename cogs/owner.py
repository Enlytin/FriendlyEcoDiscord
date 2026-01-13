import discord
from discord.ext import commands
import sys
import os
from typing import Optional, Literal

# REPLACE THIS WITH YOUR USER ID
OWNER_ID = 120052885319974912

class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # This special check runs before EVERY command in this Cog.
    # If the user is not you, the command simply fails silently or raises an error.
    async def cog_check(self, ctx):
        return ctx.author.id == OWNER_ID

    # --- COG MANAGEMENT ---

    @commands.command(name="load", hidden=True)
    async def load_cog(self, ctx, *, cog: str):
        """Loads a specific cog."""
        try:
            await self.bot.load_extension(cog)
            await ctx.message.add_reaction("✅")
            await ctx.send(f"Loaded `{cog}`")
        except Exception as e:
            await ctx.send(f"**Error:** {type(e).__name__} - {e}")

    @commands.command(name="unload", hidden=True)
    async def unload_cog(self, ctx, *, cog: str):
        """Unloads a specific cog."""
        try:
            await self.bot.unload_extension(cog)
            await ctx.message.add_reaction("✅")
            await ctx.send(f"Unloaded `{cog}`")
        except Exception as e:
            await ctx.send(f"**Error:** {type(e).__name__} - {e}")

    @commands.command(name="reload", hidden=True)
    async def reload_cog(self, ctx, *, cog: str):
        """Reloads a specific cog."""
        try:
            await self.bot.reload_extension(cog)
            await ctx.message.add_reaction("🔄")
            await ctx.send(f"Reloaded `{cog}`")
        except Exception as e:
            await ctx.send(f"**Error:** {type(e).__name__} - {e}")

    # --- BOT LIFECYCLE ---

    @commands.command(name="shutdown", hidden=True)
    async def shutdown(self, ctx):
        """Shuts down the bot entirely."""
        await ctx.send("👋 Shutting down...")
        await self.bot.close()

    @commands.command(name="restart", hidden=True)
    async def restart(self, ctx):
        """Restarts the bot process."""
        await ctx.send("🔁 Restarting...")
        # This replaces the current process with a new one using the same arguments
        os.execv(sys.executable, ['python'] + sys.argv)

    # --- SYNC COMMAND (Essential for Slash Commands) ---

    @commands.command(name="sync", hidden=True)
    async def sync(self, ctx, guilds: commands.Greedy[discord.Object], spec: Optional[Literal["~", "*", "^"]] = None):
        """
        Syncs slash commands to Discord.
        Usage:
        !sync -> global sync
        !sync ~ -> sync current guild
        !sync * -> copy global to current guild
        !sync ^ -> clear current guild
        """
        if not guilds:
            if spec == "~":
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "*":
                ctx.bot.tree.copy_global_to(guild=ctx.guild)
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "^":
                ctx.bot.tree.clear_commands(guild=ctx.guild)
                await ctx.bot.tree.sync(guild=ctx.guild)
                synced = []
            else:
                synced = await ctx.bot.tree.sync()

            await ctx.send(f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild'}.")
            return

        ret = 0
        for guild in guilds:
            try:
                await ctx.bot.tree.sync(guild=guild)
            except discord.HTTPException:
                pass
            else:
                ret += 1
        await ctx.send(f"Synced the tree to {ret}/{len(guilds)} guilds.")

    # --- GUILD ADMINISTRATION ---

    @commands.command(name="leave", hidden=True)
    async def leave_guild(self, ctx, guild_id: int = None):
        """Forces the bot to leave a guild."""
        # Use current guild if no ID provided
        if guild_id is None:
            guild = ctx.guild
        else:
            guild = self.bot.get_guild(guild_id)

        if guild:
            await guild.leave()
            await ctx.send(f"Left guild: {guild.name} ({guild.id})")
        else:
            await ctx.send("Could not find that guild.")

    @commands.command(name="servers", hidden=True)
    async def list_servers(self, ctx):
        """Lists the top 10 servers by member count."""
        guilds = sorted(self.bot.guilds, key=lambda g: g.member_count, reverse=True)
        msg = "**Top Guilds:**\n"
        for g in guilds[:10]:
            msg += f"• {g.name} (`{g.id}`) - {g.member_count} members\n"
        await ctx.send(msg)

async def setup(bot):
    await bot.add_cog(Owner(bot))