# import statements
import os
import json
import discord
from replit import db
from discord.ext import commands
intents = discord.Intents(messages=True, guilds=True, members=True)
from datetime import datetime
from keepalive import keep_alive

# import helper files
import postData
import processMessage

# declare variables
bot = commands.Bot("$")
bot.remove_command('help')
log_type = 'MessageLogs'
auditLog_type = 'DiscordAuditLogs'
client = discord.Client(intents=intents)

# Discord client is active
@client.event
async def on_ready():
  # print(client.guild.me.guild_permissions)
  print('We have logged in...')

# @bot.command
# async def help(ctx):
#   print("help")
#   await bot.send_message("test")

# Log new channel creation in discord server
@client.event
async def on_guild_channel_create(channel):
  print(channel, "has just been created by ")
  userObj = await channel.guild.audit_logs(action=discord.AuditLogAction.channel_create, limt=None, oldest_first=False).get()
  print(userObj.user)

  await postData.post_data(db[str(channel.guild.id)+"_customer_id"], db[str(channel.guild.id)+"_shared_key"], json.dumps({"type": "ChannelCreate", "name": str(channel.name), "time": str(datetime.utcnow()), "ExtendedProperties": str(userObj.user)}), auditLog_type)


# Log channel deletion in discord server
@client.event
async def on_guild_channel_delete(channel):
  print(channel, "had just been deleted by ")
  userObj = await channel.guild.audit_logs(action=discord.AuditLogAction.channel_delete, limt=None, oldest_first=False).get()
  print(userObj.user)
  await postData.post_data(db[str(channel.guild.id)+"_customer_id"], db[str(channel.guild.id)+"_shared_key"], json.dumps({"type": "ChannelDelete", "name": str(channel.name), "time": str(datetime.utcnow()), "ExtendedProperties": str(userObj.user)}), auditLog_type)


# Log new role creation in discord server
@client.event
async def on_guild_role_create(role):
  print("created new role: ", role, " by")
  userObj = await role.guild.audit_logs(action=discord.AuditLogAction.role_create, limt=None, oldest_first=False).get()
  print(userObj.user)
  await postData.post_data(db[str(role.guild.id)+"_customer_id"], db[str(role.guild.id)+"_shared_key"], json.dumps({"type": "CreateRole", "name": str(role.name), "time": str(datetime.utcnow()), "ExtendedProperties": str(userObj.user)}), auditLog_type)


# Log role updation in discord server
@client.event
async def on_guild_role_update(before, after):
  print("role updated: ", before, after, " by")
  userObj = await after.guild.audit_logs(action=discord.AuditLogAction.role_update, limt=None, oldest_first=False).get()
  print(userObj.user)
  await postData.post_data(db[str(after.guild.id)+"_customer_id"], db[str(after.guild.id)+"_shared_key"], json.dumps({"type": "UpdateRole", "name": str(after.name), "time": str(datetime.utcnow()), "ExtendedProperties": str(userObj.user)}), auditLog_type)

  # Log if admin permissions are granted/revoked to the role
  if( (before.permissions.administrator) and (not after.permissions.administrator) ):
    print("Admin privileges removed for role: ", after, " by ", userObj.user)
    await postData.post_data(db[str(after.guild.id)+"_customer_id"], db[str(after.guild.id)+"_shared_key"], json.dumps({"type": "RevokeAdminToRole", "name": str(after.name), "time": str(datetime.utcnow()), "ExtendedProperties": str(userObj.user)}), auditLog_type)
  elif ( (after.permissions.administrator) and (not before.permissions.administrator) ):
    print("Admin privileges assigned for role: ", after, " by ", userObj.user)
    await postData.post_data(db[str(after.guild.id)+"_customer_id"], db[str(after.guild.id)+"_shared_key"], json.dumps({"type": "GrantAdminToRole", "name": str(after.name), "time": str(datetime.utcnow()), "ExtendedProperties": str(userObj.user)}), auditLog_type)

  # Log if permission to ban members is granted to the role
  if ( (after.permissions.ban_members) and (not before.permissions.ban_members) ):
    print("Ban member privileges assigned for role: ", after, " by ", userObj.user)
    await postData.post_data(db[str(after.guild.id)+"_customer_id"], db[str(after.guild.id)+"_shared_key"], json.dumps({"type": "GrantBanMemberToRole", "name": str(after.name), "time": str(datetime.utcnow()), "ExtendedProperties": str(userObj.user)}), auditLog_type)


# Log role deletion in discord server
@client.event
async def on_guild_role_delete(role):
  print("deleted role: ", role, " by ")
  userObj = await role.guild.audit_logs(action=discord.AuditLogAction.role_delete, limt=None, oldest_first=False).get()
  print(userObj.user)
  await postData.post_data(db[str(role.guild.id)+"_customer_id"], db[str(role.guild.id)+"_shared_key"], json.dumps({"type": "DeleteRole", "name": str(role.name), "time": str(datetime.utcnow()), "ExtendedProperties": str(userObj.user)}), auditLog_type)


# Log when new member/bot joins the server
@client.event
async def on_member_join(member):
  assignee = await client.fetch_user(member.id)
  if (member.bot):
    print("New bot added: ", member)
    print("Bot creation date: ", member.created_at)
    await postData.post_data(db[str(member.guild.id)+"_customer_id"], db[str(member.guild.id)+"_shared_key"], json.dumps({"type": "BotJoined", "name": str(assignee), "time": str(member.created_at)}), auditLog_type)
  else:
    print("New member joined: ", member)
    print("New member's account created on: ", member.created_at)
    await postData.post_data(db[str(member.guild.id)+"_customer_id"], db[str(member.guild.id)+"_shared_key"], json.dumps({"type": "MemberJoined", "name": str(assignee), "time": str(member.created_at)}), auditLog_type)


# Log member's permission updates
@client.event
async def on_member_update(before, after):
  beforeRole = len(before.roles)
  afterRole = len(after.roles)
  userObj = await after.guild.audit_logs(action=discord.AuditLogAction.role_update, limit=None, oldest_first=True).get()
  print(userObj)
  assignee = await client.fetch_user(after.id)
  if(afterRole-beforeRole > 0):
    print("new role added to user ", str(assignee), " by ", userObj.user)
    await postData.post_data(db[str(after.guild.id)+"_customer_id"], db[str(after.guild.id)+"_shared_key"], json.dumps({"type": "RoleAddToMember", "name": str(assignee), "time": str(datetime.utcnow()), "ExtendedProperties": str(userObj.user)}), auditLog_type)
  elif (afterRole-beforeRole < 0):
    print("role removed for user ", str(assignee), " by ", userObj.user)
    await postData.post_data(db[str(after.guild.id)+"_customer_id"], db[str(after.guild.id)+"_shared_key"], json.dumps({"type": "RoleRemoveToMember", "name": str(assignee), "time": str(datetime.utcnow()), "ExtendedProperties": str(userObj.user)}), auditLog_type)

  befAdmin = False
  aftAdmin = False
  befBan = False
  aftBan = False

  for i in before.roles:
    if (i.permissions.administrator):
      befAdmin = True
    if (i.permissions.ban_members):
      befBan = True

  for i in after.roles:
    if (i.permissions.administrator):
      aftAdmin = True
    if (i.permissions.ban_members):
      aftBan = True

  # Log if admin privileges are granted/revoked to user
  if ( (befAdmin) and (not aftAdmin) ):
    print("Admin privileges removed for user: ", str(assignee), " by ", userObj.user)
    await postData.post_data(db[str(after.guild.id)+"_customer_id"], db[str(after.guild.id)+"_shared_key"], json.dumps({"type": "RevokeAdminToUser", "name": str(assignee), "time": str(datetime.utcnow()), "ExtendedProperties": str(userObj.user)}), auditLog_type)
  elif ( (aftAdmin) and (not befAdmin) ):
    print("Admin privileges assigned for user: ", str(assignee), " by ", userObj.user)
    await postData.post_data(db[str(after.guild.id)+"_customer_id"], db[str(after.guild.id)+"_shared_key"], json.dumps({"type": "GrantAdminToUser", "name": str(assignee), "time": str(datetime.utcnow()), "ExtendedProperties": str(userObj.user)}), auditLog_type)

  # Log if permission to ban members is granted to user
  if ( (aftBan) and (not befBan) ):
    print("Ban members privileges assigned for user: ", str(assignee), " by ", userObj.user)
    await postData.post_data(db[str(after.guild.id)+"_customer_id"], db[str(after.guild.id)+"_shared_key"], json.dumps({"type": "GrantBanMemberToUser", "name": str(assignee), "time": str(datetime.utcnow()), "ExtendedProperties": str(userObj.user)}), auditLog_type)


# Log when a message is sent in discord
@client.event
async def on_message(message):
  def check(event):
    return event.target.id == bot.user.id

  # Do not log messages by this client bot    
  if message.author == client.user:
    return

  await processMessage.analyzeMessage(message)

keep_alive()
client.run(os.environ['Bot_secret'])