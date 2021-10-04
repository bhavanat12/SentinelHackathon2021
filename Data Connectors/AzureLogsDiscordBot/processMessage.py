# import statements
import json
import requests
from replit import db
from datetime import datetime, timedelta
from urlextract import URLExtract
from urllib.parse import urlparse
from discord import Embed, Color

# import helper file
import postData

# declare variables
extractor = URLExtract()
log_type = 'MessageLogs'
auditLog_type = 'DiscordAuditLogs'


async def analyzeAttachmentsAndUrls(message):
      print(message.channel.guild.me.guild_permissions)
      print(message.content)
      print(message.author)

      # Process urls if any in the message
      isUrlAttach = False
      urls = extractor.find_urls(message.content)
      domain =""
      if urls:
        domain = urlparse(urls[0]).netloc
        if domain == 'cdn.discordapp.com':
          isUrlAttach = True
        url_count = len(urls)
      else:
        url_count = 0
      
      for attachUrl in urls:
        # Check if any newly joined user is immediately sharing links

        if isUrlAttach:
          continue

        authUser = message.author
        serverJoinTime = message.author.joined_at
        print(authUser, " joined server at ", serverJoinTime)
        now_utc = datetime.utcnow()
        if (now_utc - serverJoinTime < timedelta(minutes = 90)):
          print("Newly joined user: %s is sharing links", authUser)
          await postData.post_data(db[str(message.guild.id)+"_workspace_id"], db[str(message.guild.id)+"_shared_key"], json.dumps({"type": "NewUserSharingLinks", "name": str(message.author), "time": str(serverJoinTime)}), auditLog_type)
        
        # Check if members are forwarding attachments within channels
        attachList = attachUrl.split("https://cdn.discordapp.com/attachments/",1)
        if (len(attachList) > 1):
          attachmentInfo = attachUrl.split("https://cdn.discordapp.com/attachments/",1)[1]
          attChannel = attachmentInfo.split('/')[0]
          if(attChannel != str(message.channel.id)):
            print("Attachment forward detected by ", message.author)
            await postData.post_data(db[str(message.guild.id)+"_workspace_id"], db[str(message.guild.id)+"_shared_key"], json.dumps({"type": "AttachmentForward", "name": str(message.author), "time": str(datetime.utcnow()), "ExtendedProperties":str(attChannel)}), auditLog_type)

      # processing attachments in message
      #2ySPKfwvK1tJvaPTd1ce/Gaekoa301xO92s6aREW5rVwDtpV8qtWHA==
      if (len(message.attachments) or isUrlAttach):
        attachmentUrl = ''
        contentTypeVal = ''
        fileSize = ''
        attachId = ''
        if isUrlAttach:
          attachmentUrl = str(message.content)
          contentTypeVal = str(message.content.split(".")[-1])
          fileSize = '0'
          attachId = str(message.id)
          fileName = str(message.content.split("/")[-1])
        else:
          attachmentUrl = str(message.attachments[0].url)
          contentTypeVal = str(message.attachments[0].content_type)
          fileSize = str(message.attachments[0].size)
          attachId = str(message.attachments[0].id)
          fileName = str(message.attachments[0].filename)
        attachment_function_url = "https://discordattachmentsstore.azurewebsites.net/api/DiscordAttachments?code="+db[str(message.guild.id)+"_function_code"]+"&cdn_url="+ attachmentUrl
        if(len(message.attachments) and message.attachments[0].filename.split(".")[-1] in db[str(message.guild.id)+"_extension_types"].value):
          await message.channel.send("Attached File has been deleted, as the file extension - ''"+ message.attachments[0].filename.split(".")[-1] + "'' has been marked as blacklisted by server admin.")
          await message.delete() # Delete the message for security purposes
        elif(isUrlAttach and attachmentUrl.split(".")[-1] in db[str(message.guild.id)+"_extension_types"].value):
          await message.channel.send("Attached File has been deleted, as the file extension - ''"+ attachmentUrl.split(".")[-1] + "'' has been marked as blacklisted by server admin.")
          await message.delete() # Delete the message for security purposes
        else:
          await message.reply("Attachment Verification in process..")

        
        obj = {
          "customer_id": str(db[str(message.guild.id)+"_workspace_id"]),
          "shared_key": str(db[str(message.guild.id)+"_shared_key"]),
          "extensions": db[str(message.guild.id)+"_extension_types"].value,
          "author": str(message.author),
          "channelid": str(message.channel.id),
          "channel":str(message.channel),
          "content_type": str(contentTypeVal),
          "attachmentid": str(attachId),
          "filesize": str(fileSize),
          "filename": str(fileName),
          "filestorage": str(db[str(message.guild.id)+"_fs_conn_str"])
        }
        jsonObj = json.dumps(obj)

        # Storing attachment in Azure Blob storage to further analyze for virus
        requests.post(
          attachment_function_url, 
          headers = {'Content-Type': 'application/json'}, 
          data = jsonObj)
        print(obj)

      # Log the message in LogAnalytics for further analysis
      print(str(message.channel.id))
      await postData.post_data(db[str(message.guild.id)+"_workspace_id"], db[str(message.guild.id)+"_shared_key"], json.dumps({"content": message.content, "author": str(message.author), "channel": str(message.channel), "url_count": url_count,"messageid": str(message.id),"channelid": str(message.channel.id), "urls": domain, "channelID": str(message.channel.id)}), log_type)


async def analyzeMessage(message):
  msg = message.content
  
  # Collecting credentials 
  if message.author.guild_permissions.administrator:
    if msg.startswith("$workspace_id"):
      data = msg.split()[1]
      db[str(message.guild.id)+"_workspace_id"] = data
      await message.channel.send("Customer id successfully stored")
      await message.delete() # Delete the message for security purposes
      print("Stored customerId")
    elif msg.startswith("$shared_key"):
      data = msg.split()[1]
      db[str(message.guild.id)+"_shared_key"] = data
      await message.channel.send("Shared Key successfully stored")
      await message.delete() # Delete the message for security purposes
      print("Stored sharedKey")
    elif msg.startswith("$extensionTypes"):
      data = msg.split()[1:]
      print(data)
      if db[str(message.guild.id)+"_extension_types"]:
        [db[str(message.guild.id)+"_extension_types"].append(i) for i in data]
      else:
        db[str(message.guild.id)+"_extension_types"] = []
        [db[str(message.guild.id)+"_extension_types"].append(i) for i in data]
      # db[str(message.guild.id)+"_extension_types"] = data
      print(db[str(message.guild.id)+"_extension_types"])
      await message.channel.send("extension types successfully stored")
      await message.delete() # Delete the message for security purposes
      print("Stored allowable extension types")
    elif msg.startswith("$function_code"):
      data = msg.split()[1]
      db[str(message.guild.id)+"_function_code"] = data
      await message.channel.send("Function Code successfully stored")
      await message.delete() # Delete the message for security purposes
      print("Function Code")
    elif msg.startswith("$filestore_connection"):
      # "DefaultEndpointsProtocol=https;AccountName=discordattachmentsstore;AccountKey=u7pKGMdxWgnh5wkuTNlgiClmE+laWR1yUW2bJ0979G+5NxuFSb56iQq8dP8mmSWxVajbGIzZKCmFiLDJHa7i0w==;EndpointSuffix=core.windows.net"
      data = msg.split()[1]
      db[str(message.guild.id)+"_fs_conn_str"] = data
      await message.channel.send("File Storage Connection String successfully stored")
      await message.delete() # Delete the message for security purposes
      print("File Storage Connection String")
    elif msg.startswith("$help"):
      e = Embed(color = Color.blurple(), description='AzureLogs Bot Help/Configuration')
      e.add_field(
        name = "List of Commands: \n",
        value = """\n$workspace_id
        \n$shared_key
        \n$extensionTypes
        \n\n$function_code
        \n\n$filestore_connection""",
        inline = True
      )
      e.add_field(
        name = "Description: \n",
        value = """\nWorkspace ID of Log Analytics Workspace
        \n Primary/Secondary Key of Log Analytics Workspace
        \n Blacklist file extensions for attachments.
        (Usage: $extensionTypes xml lmz)
        \n Function Key of Azure Function Deployed in Discord Attachments App.
        \n Connection String of the Storage Account used for Attachments""",
        inline = True
      )
      await message.channel.send(embed=e)
    else:
      await analyzeAttachmentsAndUrls(message)
  else:
    # process messages for non-admin user
    await analyzeAttachmentsAndUrls(message)
    