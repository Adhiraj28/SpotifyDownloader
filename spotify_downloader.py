import spotipy
from spotipy.oauth2 import SpotifyOAuth
from googleapiclient.discovery import build
from pytube import YouTube
import os, shutil 
from moviepy.editor import *

# Spotify setup
def get_spotify_client():
    # Replace 'your_client_id' and 'your_client_secret' with your Spotify API credentials
    return spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="your_client_id",
                                                     client_secret="your_client_secret",
                                                     redirect_uri="http://localhost:8888/callback",
                                                     scope="user-library-read"))

# Get tracks from a Spotify playlist
def get_playlist_tracks(sp, playlist_id):
    results = sp.playlist_tracks(playlist_id)
    tracks = results['items']
    
    # Paging through results if more than one page
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    
    return tracks

# YouTube search
def youtube_search(query, api_key):
    # Replace 'your_api_key' with your YouTube Data API key
    youtube = build('youtube', 'v3', developerKey='your_api_key')
    search_response = youtube.search().list(q=query, part='id,snippet', maxResults=1, type='video').execute()
    videos = []
    
    # Extracting video URLs
    for search_result in search_response.get('items', []):
        videos.append(f"https://www.youtube.com/watch?v={search_result['id']['videoId']}")

    return videos

# Download YouTube video as MP3
def download_video_as_mp3(url, path='Downloads'):
    yt = YouTube(url)
    video = yt.streams.filter(only_audio=True).first()
    out_file = video.download(output_path=path)

    # Convert to MP3 using moviepy
    base, ext = os.path.splitext(out_file)
    new_file = base + '.mp3'
    
    audioclip = AudioFileClip(out_file)
    audioclip.write_audiofile(new_file)
    audioclip.close()

    # Cleaning up
    os.remove(out_file)
    print(f"Downloaded and converted to MP3: {yt.title}")

    return new_file

# Copy MP3 to iTunes
def copy_to_itunes(file_path, itunes_auto_add_folder):
    try:
        shutil.copy(file_path, itunes_auto_add_folder)
        print(f"Copied {file_path} to iTunes.")
    except Exception as e:
        print(f"Failed to copy {file_path} to iTunes: {e}")

# Main script
def main():
    sp = get_spotify_client()
    # Replace with your playlist ID
    playlist_id = 'your_playlist_id'
    tracks = get_playlist_tracks(sp, playlist_id)
    # Replace with your YouTube API key
    api_key = 'your_api_key'
    # Replace with the path to your iTunes auto-add folder
    itunes_auto_add_folder = 'path_to_itunes_auto_add_folder'

    for item in tracks:
        track = item['track']
        query = f"{track['artists'][0]['name']} {track['name']}"
        video_urls = youtube_search(query, api_key)

        if video_urls:
            print(f"Spotify Track: {track['name']} by {track['artists'][0]['name']}")
            print(f"YouTube URL: {video_urls[0]}")

            mp3_file_path = download_video_as_mp3(video_urls[0])
            copy_to_itunes(mp3_file_path, itunes_auto_add_folder)
        else:
            print(f"No YouTube result found for {track['name']} by {track['artists'][0]['name']}")

    print("Finished processing all tracks.")

if __name__ == "__main__":
    main()
