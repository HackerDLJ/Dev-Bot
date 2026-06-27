import discord
from discord.ext import commands

class CreedSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Templer", description="Join the Templer order", emoji="🛡️"),
            discord.SelectOption(label="Assassin", description="Join the Assassin brotherhood", emoji="🗡️")
        ]
        super().__init__(placeholder="Choose your path...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        # 1. Get the roles
        role = discord.utils.get(interaction.guild.roles, name=self.values[0])
        other_role_name = "Assassin" if self.values[0] == "Templer" else "Templer"
        other_role = discord.utils.get(interaction.guild.roles, name=other_role_name)

        if not role:
            await interaction.response.send_message("Error: Role not found on server.", ephemeral=True)
            return

        # 2. Add the chosen role
        await interaction.user.add_roles(role)
        
        # 3. Remove the other role (if they have it)
        if other_role and other_role in interaction.user.roles:
            await interaction.user.remove_roles(other_role)

        await interaction.response.send_message(f"You have joined the **{self.values[0]}**!", ephemeral=True)

class CreedView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) # Persistent view
        self.add_item(CreedSelect())

class CreedPicker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setup_creed(self, ctx):
        """Use this command to post the Creed Picker!"""
        await ctx.send("🛡️ **Choose your Creed:**\nSelect an option below to gain your role:", view=CreedView())

async def setup(bot):
    await bot.add_cog(CreedPicker(bot))