import discord
from discord.ext import commands

class Debug(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    @commands.is_owner()
    async def debug403(self, ctx, member: discord.Member = None):
        """Diagnose why we can't affect someone"""
        if member is None:
            member = ctx.author
        
        bot_top_role = ctx.guild.me.top_role
        member_top_role = member.top_role
        
        embed = discord.Embed(title="Permission Debug", color=0xff0000)
        embed.add_field(name="Bot's Top Role Position", value=bot_top_role.position)
        embed.add_field(name="Target's Top Role Position", value=member_top_role.position)
        embed.add_field(name="Can Bot Affect Target?", value=bot_top_role > member_top_role)
        embed.add_field(name="Is Target Server Owner?", value=member == ctx.guild.owner)
        embed.add_field(name="Bot Has Admin?", value=ctx.guild.me.guild_permissions.administrator)
        
        await ctx.send(embed=embed)