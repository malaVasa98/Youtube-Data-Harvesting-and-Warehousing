# SQL QUERIES - the query commands are returned by the functions

# 1) What are the name of all the videos and their corresponding Channels?
def query_1():
    return '''select Channel_data.Channel_name,Video_data.Video_name
                          from Video_data
                          join Channel_data on Channel_data.Playlist_id=Video_data.Playlist_id'''

# 2) Which channels have the most number of videos, and how many videos do they have?
def query_2():
    return '''select channel_name,
                          (select count(playlist_id) 
                          from video_data where playlist_id=Channel_data.playlist_id) as videos_count
                          from Channel_data where videos_count>100 order by videos_count desc '''

# 3) What are the top 10 most viewed videos and their respective channels?
def query_3():
    return '''select Channel_data.Channel_name,Top10.video_name,Top10.video_view_count,Top10.row_num
                          from  (
                          select *, row_number() over(partition by Playlist_id order by Video_view_count desc)
                          as row_num
                          from Video_data
                          ) as Top10
                          left join Channel_data on Top10.Playlist_id=Channel_data.Playlist_id
                          where Top10.row_num<=10'''

# 4) How many comments were made on each video, and what are their corresponding video names?
def query_4():
    return '''select video_name,video_comment_count from video_data'''

# 5) Which videos have the highest number of likes, and what are their corresponding channel names?
def query_5():
    return '''select Channel_data.Channel_name,Vid_table.video_name,
                          Vid_table.max_likes
                           from (
                           select playlist_id,video_name,max(video_like_count) as max_likes
                           from video_data group by playlist_id ) as Vid_table
                           join Channel_data on Channel_data.Playlist_id=Vid_table.Playlist_id'''

# 6) What is the total number of likes for each video, and what are their corresponding video names?
def query_6():
    return '''select video_name,video_like_count from video_data'''

#7) What is the total number of views for each channel, and what are their corresponding channel names?
def query_7():
    return '''select Channel_name, Channel_views from Channel_data'''

# 8) What are the names of all the channels that have published videos in the year 2022?
def query_8():
    return '''with Table_2022 as (
                            select Playlist_id,Video_published_at from Video_data
                            where strftime("%Y",Video_published_at)=="2022"
                            ) 
                          select Channel_name
                          from (
                          select Channel_name,
                          (select count(Video_Published_at)
                          from Table_2022 where playlist_id=Channel_data.Playlist_id)
                          as Videos_2022
                          from Channel_data where Videos_2022>0)'''

# 9) What is the average duration of all videos in each channel, and what are their corresponding channel names?
def query_9():
    return '''select Channel_name,
                          (select avg(Video_duration) from video_data 
                          where Playlist_id=Channel_data.Playlist_id) as Average_duration_of_videos
                          from Channel_data'''

# 10) Which videos have the highest number of comments, and what are their corresponding channel names?
def query_10():
    return '''select Channel_data.Channel_name,Vid_table.video_name,
                          Vid_table.comment_likes
                           from (
                           select playlist_id,video_name,max(video_comment_count) as comment_likes
                           from video_data group by playlist_id ) as Vid_table
                           join Channel_data on Channel_data.Playlist_id=Vid_table.Playlist_id'''

