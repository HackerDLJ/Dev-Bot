import discord
from discord.ext import commands
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load the hidden keys from the .env file
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
API_KEY = os.getenv("API_KEY")

# Configure Gemini
genai.configure(api_key=API_KEY)

# ... (the rest of your code stays the same) ...

# --- SYSTEM IDENTITY (Developer's Creed Persona) ---
system_prompt = """
You are Dev Bot, the official AI assistant of the "Developer's Creed" Discord server (ID: 931936721703174225). 
You were created by DLJ to serve as the community's primary coding mentor and technical companion.

YOUR MISSION:
1. Programming Excellence: Help members with coding, debugging, and architecture. Always suggest clean, secure, and modern code practices.
2. Community Guide: Be the heartbeat of the Developers Creed. If a user asks about the server, share our invite link: https://discord.gg/4BwtHqMT.
3. Tone & Personality: Your personality is professional, encouraging, and highly analytical. You don't just give answers; you explain the "why" so members can grow. 
   - Never be lazy with code explanations.
   - If a request is unclear, ask for clarification before guessing.
   - Always maintain a "Developer's Creed" ethos: disciplined, precise, and supportive of fellow developers.

SERVER CONTEXT:
- Creator: DLJ
- Server Name: Developer's Creed
- Server ID: 931936721703174225
- Focus: A community dedicated to software development, growth, and clean code.

When answering, if the topic involves specific coding languages, try to provide snippets that are commented and optimized for performance. Keep the atmosphere welcoming.
"""

# Initialize the model
model = genai.GenerativeModel(
    model_name='models/gemini-2.5-flash',
    system_instruction=system_prompt
)

# Dictionary to store chat memory for each user
user_chats = {}

# --- BOT SETUP ---
# --- BOT SETUP ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # This is the line you were missing!
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    await bot.load_extension('creed_picker')
    await bot.change_presence(activity=discord.Game(name="Coding for Developers Creed"))
    print(f'--- devBot (created by DLJ) is now online ---')

# --- COMMANDS ---
@bot.command()
async def serverinfo(ctx):
    """Fetches insights about the Developers Creed server."""
    guild = ctx.guild
    embed = discord.Embed(title=f"Insights for {guild.name}", color=discord.Color.blue())
    embed.add_field(name="Owner", value=guild.owner.name, inline=True)
    embed.add_field(name="Member Count", value=guild.member_count, inline=True)
    embed.add_field(name="Created At", value=guild.created_at.strftime("%B %d, %Y"), inline=True)
    embed.add_field(name="Invite Link", value="https://discord.gg/4BwtHqMT", inline=False)
    await ctx.send(embed=embed)

# --- AI CHAT LOGIC ---
@bot.event
async def on_message(message):
    # Prevent the bot from replying to itself
    if message.author == bot.user:
        return

    # Check if the bot was tagged
    if bot.user.mentioned_in(message):
        user_id = message.author.id
        
        # Start a new chat session for this user if one doesn't exist
        if user_id not in user_chats:
            user_chats[user_id] = model.start_chat(history=[])
        
        # Clean the message content (remove the mention)
        user_question = message.content.replace(f'<@{bot.user.id}>', '').strip()
        
        if not user_question:
            await message.reply("Hello! How can I assist you with your code today?")
            return

        # Show "typing..." indicator
        async with message.channel.typing():
            try:
                # Send the message to the AI (with memory)
                response = user_chats[user_id].send_message(user_question)
                
                # Truncate response if it exceeds Discord limit (2000 chars)
                reply_text = response.text
                if len(reply_text) > 2000:
                    reply_text = reply_text[:1995] + "..."
                
                await message.reply(reply_text)
            except Exception as e:
                await message.reply("I'm having trouble connecting to the logic core. Please try again.")
                print(f"Error: {e}")

    # Required to allow commands like !serverinfo to work
    await bot.process_commands(message)

# --- RUN THE BOT ---
bot.run(DISCORD_TOKEN)