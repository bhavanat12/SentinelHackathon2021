# SentinelHackathon2021

### Code Deployment:
1. The ARM templates corresponding to the Hunting Queries, Analytic Rules, Workbooks, Playbooks are given in the respective folders.
2. Upload each of these templates to create the resources
3. In order to track the Discord alerts sent by our Bot, follow the below steps:
   - Create a private channel where you want the Discord alerts to be displayed
   - Go to server settings -> Integrations -> New Webhook and select the channel that you created in step 1
   - Copy the Webhook URL and paste this value while uploading the ARM template for Playbooks


### Configuration:

1. Add the AzureLogsBot from [Bot Link](https://discord.com/api/oauth2/authorize?client_id=883646665473540117&permissions=8&scope=bot%20applications.commands) to your server
2. Type $help in the server to get instructions related to Sentinel solution configuration

![Screenshot (135)](https://user-images.githubusercontent.com/56287147/135886356-f3b84fa9-4f38-47c9-8584-88826787acc4.png)

3. Get the Workspace ID and shared key from the LogAnalytics Workspace (LogAnalytics Workspace -> Agents management, copy workspace id and primary key correspondingly )
4. Define the blacklisted extensionTypes (ex: xml, lmz etc)
5. Create a function app with a HTTP trigger. Update the default \_\_init\_\_.py file with contents of [AttachmentParse.py](https://github.com/bhavanat12/SentinelHackathon2021/blob/master/Data%20Connectors/AttachmentsFunctionApp/AttachmentParse.py).
6. Get the function key of Azure function deployed in Azure.
7. Create a storage account for blob storage, get the connection string of the storage account.
8. Navigate to Data Connectors in Azure Sentinel and enable the Azure Defender Connector.
