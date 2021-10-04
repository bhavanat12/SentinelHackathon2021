# SentinelHackathon2021

### Code Deployment:
1. The ARM templates corresponding to the Hunting Queries, Analytic Rules, Workbooks, Playbooks are given in the respective folders.
2. Upload each of these templates to create the resources


### Configuration:

1. Add the AzureLogsBot from marketplace to your server
2. Type $help in the server to get instructions related to Sentinel solution configuration
![Screenshot](Screenshot (135).png)
3. Get the Workspace ID and shared key from the LogAnalytics Workspace (LogAnalytics Workspace -> Agents management, copy workspace id and primary key correspondingly )
4. Define the Blocklisted extensionTypes (ex: xml, lmz etc)
5. Get the function key of Azure function deployed in Azure
6. Get the connection string of the storage account
