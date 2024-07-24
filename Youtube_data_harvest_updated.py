# Before running this code make sure to run this code in the terminal pip install streamlit and also pip install google-api-python-client. If both are already installed then proceed with running the code
import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import csv
import os
st.title(":red[Youtube Data Harvesting and Warehousing]")

# using user defined API key to access the Youtube API v3
import googleapiclient.discovery
api_service_name = "youtube"
api_version = "v3"
api_key = "AIzaSyCmp8iWBi787Op3gV_G-bq9P2q2B0NIqKE"
youtube = googleapiclient.discovery.build(api_service_name, api_version,developerKey=api_key)

# Channel_published_at / Video_published_at is in string format as given by format_string, this function file with convert it to date time format
from datetime import datetime
def date_time(strn):
    format_string = ["%Y-%m-%dT%H:%M:%S.%fZ","%Y-%m-%dT%H:%M:%SZ"]
    for format_str in format_string:
        try:
            formatted_date = datetime.strptime(strn,format_str)
            break
        except ValueError:
            continue
    return formatted_date

# To convert the duration of the video into (int) seconds
import re
def duration_to_seconds(dur):
    if 'H' in dur:
        if ('S' in dur)and('M' in dur):
            pattern = re.compile(r'PT(\d+)H(\d+)M(\d+)S')
            match = pattern.match(dur)
            if match:
                hours = int(match.group(1))
                minutes = int(match.group(2))
                seconds = int(match.group(3))
                total_seconds = hours*3600+minutes * 60 + seconds
                return total_seconds
            else:
                return None
        elif 'S' not in dur:
            pattern = re.compile(r'PT(\d+)H(\d+)M')
            match = pattern.match(dur)
            if match:
                hours = int(match.group(1))
                minutes = int(match.group(2))
                total_seconds = hours*3600+minutes*60
                return total_seconds
            else:
                return None
        else:
            pattern = re.compile(r'PT(\d+)H(\d+)S')
            match = pattern.match(dur)
            if match:
                hours=int(match.group(1))
                seconds = int(match.group(2))
                total_seconds = hours*3600+seconds
                return total_seconds
            else:
                return None
    else:
        if ('S' in dur)and('M' in dur):
            pattern = re.compile(r'PT(\d+)M(\d+)S')
            match = pattern.match(dur)
            if match:
                minutes = int(match.group(1))
                seconds = int(match.group(2))
                total_seconds = minutes * 60 + seconds
                return total_seconds
            else:
                return None
        elif 'S' not in dur:
            pattern = re.compile(r'PT(\d+)M')
            match = pattern.match(dur)
            if match:
                minutes = int(match.group(1))
                total_seconds = minutes*60
                return total_seconds
            else:
                return None
        else:
            pattern = re.compile(r'PT(\d+)S')
            match = pattern.match(dur)
            if match:
                seconds = int(match.group(1))
                total_seconds = seconds
                return total_seconds
            else:
                return None

# Getting Channel details
def channel_data(c_id):
    request = youtube.channels().list(
        part="snippet,contentDetails,statistics",
        id=c_id
    )
    response = request.execute()
    data = {"Channel_name":response['items'][0]['snippet']['title'],
            "Channel_id":c_id,
            "Channel_description":response['items'][0]['snippet']['description'],
            "Channel_published_at":date_time(response['items'][0]['snippet']['publishedAt']),
            "Playlist_id":response['items'][0]['contentDetails']['relatedPlaylists']['uploads'],
            "Subscription_Count":int(response['items'][0]['statistics']['subscriberCount']),
            "Channel_views":int(response['items'][0]['statistics']['viewCount'])
        
    }
    return data

Channel_name = []
Channel_id = []
Channel_description = []
Channel_published_at = []
Playlist_id = []
Subscription_Count = []
Channel_views = []
# Video Details
def video_id_data(c_id):
    video_id = []
    Playlist_id_vid = []
    p_id = channel_data(c_id)
    next_page_token=None
    while True:
        request = youtube.playlistItems().list(
            part="snippet,contentDetails",
            playlistId=p_id["Playlist_id"],
            maxResults=50,
            pageToken=next_page_token
            )
        response = request.execute()
        l_a = []
        for item in response['items']:
            video_id.append(item['contentDetails']['videoId'])
            l_a.append(item['contentDetails']['videoId'])
        next_page_token = response.get('nextPageToken')
        Playlist_id_vid = Playlist_id_vid + [p_id["Playlist_id"] for count in range(len(l_a))]
        if not next_page_token:
            break
    return video_id,Playlist_id_vid

# Obtaining Video Data
def video_data(idx): 
        request = youtube.videos().list(
                part="snippet,contentDetails,statistics",
                id=idx
                )
        response = request.execute()
        vid_data = {
            "Video_name":response['items'][0]['snippet']['title'],
            "Video_description":response['items'][0]['snippet']['description'],
            "Video_Published_at":date_time(response['items'][0]['snippet']['publishedAt']),
            "Video_view_count":int(response['items'][0]['statistics']['viewCount']),
            "Video_like_count":int(response['items'][0]['statistics']['likeCount']) if 'likeCount' in response['items'][0]['statistics'].keys() else None,
            "Video_favorite_count":int(response['items'][0]['statistics']['favoriteCount']),
            "Video_comment_count":int(response['items'][0]['statistics']['commentCount']),
            "Video_duration":duration_to_seconds(response['items'][0]['contentDetails']['duration']),
            "Video_thumbnail":response['items'][0]['snippet']['thumbnails']['default']['url'],
            "Video_caption_status":"Not Available" if response['items'][0]['contentDetails']['caption']=='false' else "Available"
        }
        return vid_data
# Getting the video details for each video id 
Video_name = []
Video_description = []
Video_Published_at = []
Video_view_count = []
Video_like_count = []
Video_favorite_count = []
Video_comment_count = []
Video_duration = []
Video_thumbnail = []
Video_caption_status = []

# Comment details for each comment id
Comment_id = []
Video_id_com = []
Comment_text = []
Comment_author = []
Comment_published_at = []

# Executing this function will give the details of the corresponding channel id
def execute_fn(c_id):
    with st.spinner('Please Wait'):
        data_ch = channel_data(c_id)
        Channel_name.append(data_ch["Channel_name"])
        Channel_id.append(data_ch["Channel_id"])
        Channel_description.append(data_ch["Channel_description"])
        Channel_published_at.append(data_ch["Channel_published_at"])
        Playlist_id.append(data_ch["Playlist_id"])
        Subscription_Count.append(data_ch["Subscription_Count"])
        Channel_views.append(data_ch["Channel_views"])
        Channel_data = {
                            "Channel_name":Channel_name,
                            "Channel_id":Channel_id,
                            "Channel_description":Channel_description,
                            "Channel_published_at":Channel_published_at,
                            "Playlist_id":Playlist_id,
                            "Subscription_Count":Subscription_Count,
                            "Channel_views":Channel_views
                            }
        df_chan = pd.DataFrame(Channel_data)
        file_path = ("Channel_data_up.csv")
        if os.path.exists(file_path):
            df_chan.to_csv('Channel_data_up.csv',mode='a',index=False,header=False)
        else:
            df_chan.to_csv("Channel_data_up.csv",index=False)
        data_vd = video_id_data(c_id)
        for idx in data_vd[0]:
            data_v = video_data(idx)
            Video_name.append(data_v["Video_name"])
            Video_description.append(data_v["Video_description"])
            Video_Published_at.append(data_v["Video_Published_at"])
            Video_view_count.append(data_v["Video_view_count"])
            Video_like_count.append(data_v["Video_like_count"])
            Video_favorite_count.append(data_v["Video_favorite_count"])
            Video_comment_count.append(data_v["Video_comment_count"])
            Video_duration.append(data_v["Video_duration"])
            Video_thumbnail.append(data_v["Video_thumbnail"])
            Video_caption_status.append(data_v["Video_caption_status"])
        Video_data = {
                            "Playlist_id":data_vd[1],
                            "Video_id":data_vd[0],
                            "Video_name":Video_name,
                            "Video_description":Video_description,
                            "Video_Published_at":Video_Published_at,
                            "Video_view_count":Video_view_count,
                            "Video_like_count":Video_like_count,
                            "Video_favorite_count":Video_favorite_count,
                            "Video_comment_count":Video_comment_count,
                            "Video_duration":Video_duration,
                            "Video_thumbnail":Video_thumbnail,
                            "Video_caption_status":Video_caption_status
                            }
        file_pathv = "Video_data_up.csv"
        df_vid = pd.DataFrame(Video_data)
        if os.path.exists(file_pathv):
            df_vid.to_csv('Video_data_up.csv',mode='a',index=False,header=False)
        else:
            df_vid.to_csv("Video_data_up.csv",index=False)
        Video_id_com = []
        for i in range(len(data_vd[0])):
            # This is because videos with O comments have no comment IDs 
            if Video_data["Video_comment_count"][i]!=0: 
                request = youtube.commentThreads().list(
                                part="id,snippet",
                                videoId=Video_data["Video_id"][i],
                                maxResults=100
                                )
                response = request.execute()
                L_a = []
                for comm in response['items']:
                    Comment_id.append(comm['id'])
                    L_a.append(comm['id'])
                    Comment_text.append(comm['snippet']['topLevelComment']['snippet']['textDisplay'])
                    Comment_author.append(comm['snippet']['topLevelComment']['snippet']['authorDisplayName'])
                    Comment_published_at.append(date_time(comm['snippet']['topLevelComment']['snippet']['publishedAt']))
                Video_id_com = Video_id_com +[Video_data["Video_id"][i] for count in range(len(L_a))]

        Comment_data = {
                            "Comment_id":Comment_id,
                            "Video_id":Video_id_com,
                            "Comment_text":Comment_text,
                            "Comment_author":Comment_author,
                            "Comment_published_at":Comment_published_at
                            }
        file_pathc='Comment_data_up.csv'
        df_comm = pd.DataFrame(Comment_data)
        if os.path.exists(file_pathc):
            df_comm.to_csv('Comment_data_up.csv',mode='a',index=False,header=False)
        else:
            df_comm.to_csv('Comment_data_up.csv',index=False)
        st.success("Uploaded successfully")

# Create 3 option menus : About the project, Data Extraction, Insert into SQL and SQL Querying
with st.sidebar:
    selected = option_menu(None,['About','Data Extraction','Migrate to SQL','SQL Queries'])
    
if selected=='About':
    st.write("The project emphasises on extracting the data from different YouTube channels like channel, video and comment details using Youtube API v3 from Google API client library and migrate them to a SQL table and then analyse the data and diplay the results in the Streamlit App")
    st.header("Approach")
    st.write("1. Use the Google API client library for Python and make the required requests to the Youtube API to obtain the required data.")
    st.write("2. After obtaining the relevant data, use pandas Dataframes to migrate them to a data warehouse")
    st.write("3. Once the data for multiple channels is obtained, the data is migarted to SQL (here SQLite3 is used).")
    st.write("4. Use the SQL query commands to perform data analysis and display the results in this app.")
if selected=='Data Extraction':
    global c_id
    c_id = st.text_input('Enter a Channel ID')
    if c_id and st.button("Extract Data"):
        data = channel_data(c_id)
        st.write('Channel Name: ',data["Channel_name"])
        st.write('Channel Description: ',data["Channel_description"])
        st.write(f'Published At: {data["Channel_published_at"]}')
        st.write(f'Subscription Count: {data["Subscription_Count"]}')
        st.write(f'Views: {data["Channel_views"]}')
    if c_id and st.button("Upload to Pandas"):
        # Before Uploading to Pandas, we need to check if the details for this channel id are already fetched
        filepath = ("Channel_data_up.csv")
        if os.path.exists(filepath):
            df_ch = pd.read_csv('Channel_data_up.csv')
            if c_id in [x for x in df_ch["Channel_id"]]:
                st.warning(f'Channel details for {c_id} already exists in the database')
            else:
                execute_fn(c_id)
        else:
            execute_fn(c_id)
        

# SQL migration
from sqlalchemy import create_engine

        
# SQL database setup
engine = create_engine('sqlite:///youtube_data.db', echo=True)
if selected=="Migrate to SQL":
    options = st.selectbox("Select table for transformation",("Channel Table","Video Table","Comment Table"),index=None)
    if options=="Channel Table":
        st.header('Channel Table')
        df_chan = pd.read_csv('Channel_data_up.csv')
        df_chan.to_sql('Channel_data',con=engine, if_exists='replace', index=False)
        ch_tb = pd.read_sql_query('''select * from Channel_data''',con=engine)
        st.dataframe(ch_tb)
    elif options=="Video Table":
        st.header('Video Table')
        df_vid = pd.read_csv('Video_data_up.csv')
        df_vid.to_sql('Video_data',con=engine,if_exists='replace',index=False)
        vd_tb = pd.read_sql_query('''select * from Video_data''',con=engine)
        st.dataframe(vd_tb,width=900,height=500)
    elif options=="Comment Table":
        st.header('Comment Table')
        df_comm = pd.read_csv('Comment_data_up.csv')
        df_comm.to_sql('Comment_data',con=engine,if_exists='replace',index=False)
        com_tb = pd.read_sql_query('''select * from Comment_data''',con=engine)
        st.dataframe(df_comm,width=900,height=500)
        
if selected=="SQL Queries":
    st.write('Analysis using SQL')
    Df_chan = pd.read_csv('Channel_data_up.csv')
    Df_chan.to_sql('Channel_data', con=engine, if_exists='replace', index=False)
    Df_vid = pd.read_csv('Video_data_up.csv')
    Df_vid.to_sql('Video_data', con=engine, if_exists='replace', index=False)
    from Sql_queries import query_1, query_2, query_3, query_4, query_5, query_6, query_7, query_8, query_9, query_10
    Sql_qns = {
               "Q1":"What are the name of all the videos and their corresponding Channels?",
               "Q2":"Which channels have the most number of videos, and how many videos do they have?",
               "Q3":"What are the top 10 most viewed videos and their respective channels?",
               "Q4":"How many comments were made on each video, and what are their corresponding video names?",
               "Q5":"Which videos have the highest number of likes, and what are their corresponding channel names?",
               "Q6":"What is the total number of likes for each video, and what are their corresponding video names?",
               "Q7":"What is the total number of views for each channel, and what are their corresponding channel names?",
               "Q8":"What are the names of all the channels that have published videos in the year 2022?",
               "Q9":"What is the average duration of all videos in each channel, and what are their corresponding channel names?",
              "Q10":"Which videos have the highest number of comments, and what are their corresponding channel names?"
                  }
    option = st.selectbox("Select an SQL query",tuple(Sql_qns.values()),index=None)
    if option==Sql_qns["Q1"]:
        res_1 = pd.read_sql_query(query_1(),con=engine)
        st.dataframe(res_1,width=900,height=500)
    elif option==Sql_qns["Q2"]:
        res_2 = pd.read_sql_query(query_2(),con=engine)
        st.dataframe(res_2,width=900,height=180)
    elif option==Sql_qns["Q3"]:
        res_3 = pd.read_sql_query(query_3(),con=engine)
        st.dataframe(res_3,width=900,height=500)
    elif option==Sql_qns["Q4"]:
        res_4 = pd.read_sql_query(query_4(),con=engine)
        st.dataframe(res_4,width=900,height=500)
    elif option==Sql_qns["Q5"]:
        res_5 = pd.read_sql_query(query_5(),con=engine)
        st.dataframe(res_5)
    elif option==Sql_qns["Q6"]:
        res_6 = pd.read_sql_query(query_6(),con=engine)
        st.dataframe(res_6,width=900,height=500)
    elif option==Sql_qns["Q7"]:
        res_7 = pd.read_sql_query(query_7(),con=engine)
        st.dataframe(res_7,width=900,height=300)
    elif option==Sql_qns["Q8"]:
        res_8 = pd.read_sql_query(query_8(),con=engine)
        st.dataframe(res_8,width=500,height=180)
    elif option==Sql_qns["Q9"]:
        res_9 = pd.read_sql_query(query_9(),con=engine)
        st.dataframe(res_9,width=900,height=300)
    elif option==Sql_qns["Q10"]:
        res_10 = pd.read_sql_query(query_10(),con=engine)
        st.dataframe(res_10)
    
        
        
        
    