						-------README-------
The attached files are Youtube_data.py, Sql_queries.py, Youtube data harvesting - Trial.ipynb, SQL Querying.ipynb, Channel_data.csv, Video_data.csv, Channel ids.txt.

Youtube_data.py is the Python file that is the main code for displaying the output via the streamlit app. 
Youtube data Harvesting - Trial.ipynb, SQL Querying.ipynb are the two trial code files for extracting channel, video and comment data and the other for SQL queries.

						  
						EXPLANATION OF THE CODE:

1. Before running the code Youtube_data.py, pip install Streamlit and google-api-python-client in the terminal. If already installed, you can proceed with the code.
2. The packages Streamlit and google-api-python-client are imported. This is because both these packages are required to run the streamlit commands and the respective YouTube API commands to get the required data. The title on the streamlit app is given using st.title() command.
3. YouTube API v3 is utilized to get the required data using the user's API key obtained through Google Developer Console.
4. When we extract each data like Channel published at, Video published at and Comment Published at, the data is obtained as a string. So we have defined a function called 'date_time' to convert this into 'datetime' datatype. For this a package called datetime is required from datetime.
5. A function called duration_to_seconds is defined as the data in Video duration is represented as a string (like 'PT3M4S'/'PT1H3M45S').This functions extracts the hours, minutes and seconds separately using the package re (regular expressions are used for identifying patterns in the string) and converts them into seconds given in integer format.
6. Next, a function called channel_data_f is defined where the input is the channel id and the output is the required details as given in the code. To get the details, the command request = youtube.channels.list(part="snippet,contentDetails,statistics",id=Channel_id) is used and then executed using request.execute(). 
7.For migrating the data to SQL database, we use the package SQLalchemy where we import certain packages as given in lines 112-114 of the code.
8. Before creating a table in SQL, we need to create a database. We use create_engine command to create the database.
9. Next a function called execute_sql_query is defined to execute an SQL command. We import a module called pandas. 
10. Next we create a class called Channel where each entries correspond to the details of the corresponding channel. 
11. Lines 144-147 correspond to creating a list of channel_ids inputed by the user.
12. Lines 150-169 are for extracting the data of the channel details corresponding to each channel id. 'channels = session.query(Channel).all()' gives us a list of objects that belong to the class Channel. With this, we can obtain the channel details for each channel.
13. In lines 175-193, we create a table called Channel_data and display it in streamlit using st.table() command which is displayed as Channel data. The Channel data is later converted to a dataframe and saved as a CSV file.
14. Lines 197-221 correspond to getting the video ids of each playlist ID using youtube.playlistItems.execute() which gives the video ids of each video. Here one execution only gives 50 videos per channel as max_results is set to 50. To obtain all the video IDs of all videos of the channel, the command given in lines 220-221 is used.
15. Lines 223-241 correspond to a function file for getting the video details for each video ID. For that, lines 224-228 I used. Lines 243-282 correspond to appending each detail of the video as a list and then creating a dictionary called Video_data. This Video_data is converted to a data frame and saved as CSV file.
16. Lines 287-319 correspond to obtaining the comment data for each video ID. Here, we only consider 100 comments per video so the maxResults is set to 100, and no page token is inserted. The process of getting the comment details is similar. the command youtube.commentThreads.list() is executed where the input is video id which returns the corresponding comment details of each of the 100 comments for a video. These lines have been commented on because the Streamlit app crashes when this part is executed due to a very large quantity of data. Also, for the SQL query part, the comment table is not utilized so this is skipped.
17. For the SQL query part, the Channel table and Video table are only considered. The SQL query part is displayed in the sidebar of Stream lit app. so, the 'with st.sidebar' command is used. First the saved CSV files are read and converted to data frame using pd.read_csv and then it's converted to SQL table as given in lines 326-329.
18. In line 330, we import 10 queries which are defined as functions in Sql_queries.py. Lines 343-373 correspond to the SQL query part. We create a select box using st.selectbox, where if one question is picked, the corresponding table output will be displayed in the sidebar of the Streamlit app. 

						INSTRUCTIONS TO BE FOLLOWED.
1. First open Youtube_data.py and pip install certain packages as given above.
2. Then go to the terminal and type streamlit run Youtube_data.py. After pressing enter, this will lead to the Streamlit App in the browser.
3. Ten boxes will be displayed. Enter each Channel ID and press the Enter key in each of the 10 boxes.
4. After that, click Scarp and Insert to SQL. The channel table and the video table will be displayed.
5. Then click the small arrow on the top left corner. A box called SQL queries will be displayed. Below that, you have 'Select an SQL query' where you have the option to pick any one of the 10 questions. Selecting the one gives the table output corresponding to the query clicked.

Note:
For sample workings refer to Youtube data harvesting - Trial.ipynb and SQL Querying.ipynb

						

 

