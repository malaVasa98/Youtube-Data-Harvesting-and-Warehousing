						  PROBLEM STATEMENT

This project emphasizes collecting data from different YouTube Channels using their corresponding Channel IDs and then, extracting the data and inserting it into SQL to perform some data analysis.

						  TECHNOLOGIES USED

Python, MySQL, Streamlit.

						      APPROACH

1. First we create a user-generated API using the Google API Client library that is available in the Google Developer Console.
2. Then, we access the YouTube API using this user-generated API as the developer key.
3. Here we have considered the channel, video, and comment details for each channel ID. 
4. So, we input the channel ID in the YouTube API, to get the corresponding details that are required.
5. After the data extraction, we insert them into SQL. Here three tables are obtained - Channel, Video, and Comment table because we have considered the channel, video, and comment details of each channel.
6. In this project, we have considered 10 different YouTube channels (If you're interested you can consider more than 10).
7. Then, data analysis is performed by answering some SQL queries.

                                                     INSTRUCTIONS

1. The 'Channel Ids.txt' contains the 10 Channel IDs used in this project.
2. Getting the Channel ID:
   2.1 Go to YouTube and type the Channel name in search to access the Channel. Or you can access that channel by clicking the channel button of the corresponding video that is being watched. 
   2.2 Then click 'more' that's given in the Channel Description.
   2.3 Once clicked, a short window is displayed called 'About'. As you scroll down you'll get Channel details.
   2.4 Below channel details, click share channel and then click copy channel ID.
3. Go to the terminal and type 'streamlit run Youtube_data_harvest_updated.py' (make sure streamlit is pip installed before running this command). 
4. Once the streamlit app is opened, use step 2 to get the Channel Id and paste the Channel ID in the box that says "Enter a Channel ID".
5. Click on 'Extract Data' to get the channel details and then click Upload to Pandas to upload it to Pandas data frame.  
6. The SQL query commands are available in 'Sql_queries.py'.
   
						

 

