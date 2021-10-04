# SentinelHackathon2021

### Code Deployment:
1. The ARM templates corresponding to the Hunting Queries, Analytic Rules, Workbooks, Playbooks are given in the respective folders.
2. Upload each of these templates to create the resources


### Configuration:

1. Add the AzureLogsBot from [Bot Link](https://discord.com/api/oauth2/authorize?client_id=883646665473540117&permissions=8&scope=bot%20applications.commands) to your server
2. Type $help in the server to get instructions related to Sentinel solution configuration

![Screenshot (135)](https://user-images.githubusercontent.com/56287147/135886356-f3b84fa9-4f38-47c9-8584-88826787acc4.png)

3. Get the Workspace ID and shared key from the LogAnalytics Workspace (LogAnalytics Workspace -> Agents management, copy workspace id and primary key correspondingly )
4. Define the Blocklisted extensionTypes (ex: xml, lmz etc)
5. Get the function key of Azure function deployed in Azure
6. Get the connection string of the storage account
