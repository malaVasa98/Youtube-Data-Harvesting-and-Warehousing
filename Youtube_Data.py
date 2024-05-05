# Before running this code make sure to run this code in the terminal pip install streamlit and also pip install google-api-python-client. If both are already installed then proceed with running the code

import streamlit as st
import pandas as pd
st.title("Youtube Data Harvesting and Warehousing")
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


# Defining a function to get the required channel details using the channel id
def channel_data_f(c_id):
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



# Migrating the data to SQL
from sqlalchemy import create_engine, Column, Integer, String, DateTime,Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQL database setup
engine = create_engine('sqlite:///youtube_data.db', echo=True)
Base = declarative_base()

# Function to define SQL queries
def execute_sql_query(qn):
    # Connect to sql database use engine defined in line 118
    # Executing the query
    return pd.read_sql(qn,con=engine)

# Creatig a Class channel where the Channel details are the attributes of this class with the 
# table name "Channel_data"
class Channel(Base):
    __tablename__ = 'Channel_data'
    Channel_name = Column(String)
    Channel_id = Column(String)
    Channel_description = Column(Text)
    Channel_published_at = Column(DateTime)
    Playlist_id = Column(String,primary_key = True)
    Subscription_Count = Column(Integer)
    Channel_views = Column(Integer)
    
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()


# Input the channel id and extract the required data
chan_ids = []
for count in range(10):
    c_id = st.text_input(f"Enter Channel id {count+1}:")
    chan_ids.append(c_id)

# Extract the data
if st.button('Scrap and Insert to SQL'):
    for c_id in chan_ids:
        existing_channel = session.query(Channel).filter_by(Channel_id=c_id).first()
       
    # To ensure unique key constraint is satisfied
        if existing_channel: 
            #st.warning(f'Channel with id {c_id} already exists. So skip insertion')
            continue
        data_ch = channel_data_f(c_id)
        channel = Channel(
              Channel_name=data_ch["Channel_name"],
              Channel_id=data_ch["Channel_id"],
              Channel_description=data_ch["Channel_description"],
              Channel_published_at=data_ch["Channel_published_at"],
              Playlist_id=data_ch["Playlist_id"],
              Subscription_Count=data_ch["Subscription_Count"],
              Channel_views=data_ch["Channel_views"]
              )
        session.add(channel)
        session.commit()


    # Display the Channel Table
    
    # object instance of the Class Channel to individually access the variables inside the class Channel
    channels = session.query(Channel).all()
    if channels:
        st.write("## Channel Table")
        channel_data = []
        for channel in channels:
            channel_data.append({
                "Channel_Name":channel.Channel_name,
                "Channel_id":channel.Channel_id,
                "Channel_description":channel.Channel_description,
                "Channel_published_at":channel.Channel_published_at,
                "Playlist_id":channel.Playlist_id,
                "Subscription_Count":channel.Subscription_Count,
                "Channel_views":channel.Channel_views
            })
        st.table(channel_data)
        df_chan = pd.DataFrame(channel_data)
        df_chan.to_csv('Channel_data.csv',index=False)
    else:
        st.write('No channels found in the database.')
         
# Now to create video table
# We need the playlist id to get the video ids for each channel
    Chan_playlist_id = []
    for c_id in chan_ids:
        data_ch = channel_data_f(c_id)
        Chan_playlist_id.append(data_ch["Playlist_id"])
    # Now to get the video ids for every videos of the Channel using the Playlist id of each channel
    video_id = []
    Playlist_id_vid = []
    for i in range(len(Chan_playlist_id)):
        next_page_token=None
        while True:
            request = youtube.playlistItems().list(
                  part="snippet,contentDetails",
                  playlistId=Chan_playlist_id[i],
                  maxResults=50,
                  pageToken=next_page_token
                )
            response = request.execute()
            l_a = []
            for item in response['items']:
                video_id.append(item['contentDetails']['videoId'])
                l_a.append(item['contentDetails']['videoId'])
            next_page_token = response.get('nextPageToken')
            Playlist_id_vid = Playlist_id_vid + [Chan_playlist_id[i] for count in range(len(l_a))]
            if not next_page_token:
                break
    # Function to get the video details of each video id
    def video_data(idx): 
        request = youtube.videos().list(
                part="snippet,contentDetails,statistics",
                id=idx
                )
        response = request.execute()
        vid_data = {
            "Video_name":response['items'][0]['snippet']['title'],
            "Video_description":response['items'][0]['snippet']['description'],
            "Video_Published_at":response['items'][0]['snippet']['publishedAt'],
            "Video_view_count":response['items'][0]['statistics']['viewCount'],
            "Video_like_count":response['items'][0]['statistics']['likeCount'] if 'likeCount' in response['items'][0]['statistics'].keys() else None,
            "Video_favorite_count":response['items'][0]['statistics']['favoriteCount'],
            "Video_comment_count":response['items'][0]['statistics']['commentCount'],
            "Video_duration":response['items'][0]['contentDetails']['duration'],
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
    for idx in video_id:
        data_v = video_data(idx)
        Video_name.append(data_v["Video_name"])
        Video_description.append(data_v["Video_description"])
        Video_Published_at.append(date_time(data_v["Video_Published_at"]))
        Video_view_count.append(int(data_v["Video_view_count"]))
        Video_like_count.append(int(data_v["Video_like_count"]) if data_v["Video_like_count"]!=None else data_v["Video_like_count"])
        Video_favorite_count.append(int(data_v["Video_favorite_count"]))
        Video_comment_count.append(int(data_v["Video_comment_count"]))
        Video_duration.append(duration_to_seconds(data_v["Video_duration"]))
        Video_thumbnail.append(data_v["Video_thumbnail"])
        Video_caption_status.append(data_v["Video_caption_status"])
    Video_data = {
        "Playlist_id":Playlist_id_vid,
        "Video_id":video_id,
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
    st.write("## Video Table")
    df_vid = pd.DataFrame(Video_data)
    df_vid.to_csv('Video_data.csv',index=False)
    st.table(df_vid)
    
    # Comment table - It has commented beacuse the comment table is taking longer time to load and the App gets crashed.
    # Also all the SQL queries are done using Channel table and Video table only
    # Now to get the comment details of each video using their video ids
    #Comment_id = []
    #Video_id_com = []
    #Comment_text = []
    #Comment_author = []
    #Comment_published_at = []
    #for i in range(len(Video_data["Video_id"])):
        # This is because videos with O comments have no comment IDs 
        #if Video_data["Video_comment_count"][i]!=0: 
            #request = youtube.commentThreads().list(
                #part="id,snippet",
                #videoId=Video_data["Video_id"][i],
                #maxResults=100
                #)
            #response = request.execute()
            #L_a = []
            #for comm in response['items']:
               # Comment_id.append(comm['id'])
                #L_a.append(comm['id'])
                #Comment_text.append(comm['snippet']['topLevelComment']['snippet']['textDisplay'])
                #Comment_author.append(comm['snippet']['topLevelComment']['snippet']['authorDisplayName'])
                #Comment_published_at.append(comm['snippet']['topLevelComment']['snippet']['publishedAt'])
            #Video_id_com = Video_id_com +[Video_data["Video_id"][i] for count in range(len(L_a))]
            
    #Comment_data = {
        #"Comment_id":Comment_id,
        #"Video_id":Video_id_com,
        #"Comment_text":Comment_text,
        #"Comment_author":Comment_author,
        #"Comment_published_at":Comment_published_at
    #}
    #Df_comm = pd.DataFrame(Comment_data)
   # st.write("## Comment Table")
   # st.table(Df_comm)
    
   # SQL queries
   # To answer the sql queries, we load the channel data and video data stored in csv file
   # and convert it to dataframe and then to SQL table
with st.sidebar:
    st.write('SQL QUERIES')
    Df_chan = pd.read_csv('Channel_data.csv')
    Df_chan.to_sql('Channel_data', con=engine, if_exists='replace', index=False)
    Df_vid = pd.read_csv('Video_data.csv')
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
        res_1 = execute_sql_query(query_1())
        st.table(res_1)
    elif option==Sql_qns["Q2"]:
        res_2 = execute_sql_query(query_2())
        st.table(res_2)
    elif option==Sql_qns["Q3"]:
        res_3 = execute_sql_query(query_3())
        st.table(res_3)
    elif option==Sql_qns["Q4"]:
        res_4 = execute_sql_query(query_4())
        st.table(res_4)
    elif option==Sql_qns["Q5"]:
        res_5 = execute_sql_query(query_5())
        st.table(res_5)
    elif option==Sql_qns["Q6"]:
        res_6 = execute_sql_query(query_6())
        st.table(res_6)
    elif option==Sql_qns["Q7"]:
        res_7 = execute_sql_query(query_7())
        st.table(res_7)
    elif option==Sql_qns["Q8"]:
        res_8 = execute_sql_query(query_8())
        st.table(res_8)
    elif option==Sql_qns["Q9"]:
        res_9 = execute_sql_query(query_9())
        st.table(res_9)
    elif option==Sql_qns["Q10"]:
        res_10 = execute_sql_query(query_10())
        st.table(res_10)
            
            
        
    
    
    
    
    

    






    



    
    