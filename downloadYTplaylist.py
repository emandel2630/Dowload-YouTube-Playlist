from pytube import YouTube
from pytube import Playlist
from tqdm import tqdm
import os
import unicodedata
import string
import sys
import requests
import eyed3
import moviepy.editor as mp
import re
from mutagen.mp4 import MP4, MP4Cover
from urllib.request import urlopen, HTTPError, URLError


#How to use:
#Must have python3 installed
#Type 'pip install pytube' in command prompt
#Type 'pip install tqdm' in command prompt
#Type 'pip install eyed3' in command prompt
#Type 'pip install moviepy' in command prompt
#Type 'pip install mutagen' in command prompt

#THE PLAYLIST MUST BE PUBLIC


valid_filename_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
char_limit = 155

def add_audio_thumbnail(url, save_path,mp3_name):
	response = requests.get(url)
	thumbnail_name = mp3_name +".jpg"

	completeThumbnailName = os.path.join(save_path,thumbnail_name)


	file = open(completeThumbnailName, "wb")
	file.write(response.content)
	file.close()

	completeMP3Name = os.path.join(save_path,mp3_name)

	audiofile = eyed3.load(completeMP3Name)
	
	audiofile.initTag()

	with open(completeThumbnailName,"rb") as cover_art:
		audiofile.tag.images.set(1, cover_art.read(), "image/jpeg")

	audiofile.tag.save(version=(2,3,0))

	os.remove(completeThumbnailName)

def add_video_thumbnail(url, save_path, mp4_name):
	response = requests.get(url)

	thumbnail_name = "thumbnail.jpg"

	completeThumbnailName = os.path.join(save_path,thumbnail_name)


	file = open(completeThumbnailName, "wb")
	file.write(response.content)
	file.close()

	cover = completeThumbnailName
	filename = os.path.join(save_path,mp4_name)

	if(filename.endswith(".mp4")):
		MP4file = MP4(filename)
		if cover.endswith('.jpg') or cover.endswith('.jpeg'):
			cover_format = 'MP4Cover.FORMAT_JPEG'
		else:
			cover_format = 'MP4Cover.FORMAT_PNG'
		with open(cover, 'rb') as f:
			albumart = MP4Cover(f.read(), imageformat=cover_format)
		MP4file['covr'] = [bytes(albumart)]
		MP4file.save(filename)

	os.remove(completeThumbnailName)

def clean_filename(filename, whitelist=valid_filename_chars):
    
    # keep only valid ascii chars
    cleaned_filename = unicodedata.normalize('NFKD', filename).encode('ASCII', 'ignore').decode()

    
    # keep only whitelisted chars
    cleaned_filename = ''.join(c for c in cleaned_filename if c in whitelist)
    cleaned_filename = " ".join(cleaned_filename.split())



    if len(cleaned_filename)>char_limit:
        print("Warning, filename truncated because it was over {}. Filenames may no longer be unique".format(char_limit))
    return cleaned_filename[:char_limit]


def video_to_audio(destination,file):
	full_path = os.path.join(destination, file)
	output_path = os.path.join(destination, os.path.splitext(file)[0] + '.mp3')
	clip = mp.AudioFileClip(full_path)
	clip.write_audiofile(output_path, verbose = False, logger = None)


#Header
print("YouTube playlist downloader")
print("Created by [E]than Mandel 5/31/2021")
print("\n")


# user inputs
print("Type 'exit' whenever prompted with an input to exit the program\n")
acceptableInput = False


while acceptableInput == False:
	print("Input Playlist URL (Example: https://www.youtube.com/playlist?list=PL9-w4RkuFlnZ1IddfPn4SBZOZZxW_1hRw)")
	playlistInput = str(input(">> "))
	if(playlistInput == 'exit'):
		sys.exit()
	if(len(playlistInput.split("?",1))>1):
		if(playlistInput.split("?",1)[0] == 'https://www.youtube.com/playlist'):
			acceptableInput = True
		else:
			print("You entered a YouTube link but not a playlist link. Look at the example to ensure you are pasting the correct link\n")
	else:
		print("You did not enter a valid playlist link\n")


acceptableInput = False

while acceptableInput == False:
	print("\nDo you want to download the playlist as video or audio files? (Type 'V' or 'A')")
	VorA = str(input(">> ")).lower()
	if(VorA == 'exit'):
		sys.exit()
	if(VorA == 'v' or VorA =='video'):
		acceptableInput = True
		print("Video was selected")
	elif(VorA =='a' or VorA == 'audio'):
		acceptableInput = True
		print("Audio was selected")
	else:
		print("That is not a valid file type")


acceptableInput = False

while acceptableInput == False:
	print("\nEnter the destination directory (hit enter for current directory) (Example: C:\\Users\\emand\\OneDrive)")
	destination = str(input(">> ")) or '.'
	if(destination == 'exit'):
		sys.exit()
	if(os.path.isdir(destination) == True):
		print("All files will be saved to " + destination)
		acceptableInput = True
	else:
		print("That is not a valid directory")

playlist = Playlist(playlistInput)

print('\nNumber Of Videos In playlist: %s' % len(playlist.video_urls))
print("\n")
files_present = os.listdir(destination)


#Downloads correct file type 
if (VorA == 'a' or VorA == 'audio'):
	filetype = ".mp3"
if(VorA == 'v' or VorA == 'video'):
	filetype = ".mp4"

download_counter=0
error_counter = 0
name_error_counter = 0


for item in tqdm(playlist.videos):
	if (VorA == 'a' or VorA == 'audio'):
		videoObject = item.streams.filter(res="720p").first()
		if(videoObject is None):
			videoObject = item.streams.filter(res="360p").first()

	if(VorA == 'v' or VorA == 'video'):
		videoObject = item.streams.filter(res="720p").first()
		if(videoObject is None):
			videoObject = item.streams.filter(res="360p").first()

	videoName = clean_filename(videoObject.title)
	if(len(videoName) != 0):
		if(videoName + filetype not in files_present):
			try: 
				out_file = videoObject.download(output_path=destination)
			except HTTPError as err:
				print(str(err.code) + " could not download " + videoName)
				error_counter += 1
			else:
				new_file = out_file.rsplit('\\',1)[0]+ "\\" + videoName + '.mp4'
				os.rename(out_file, new_file)
				if(VorA == 'a' or VorA == 'audio'):
					video_to_audio(destination, new_file)
					add_audio_thumbnail(item.thumbnail_url, destination, (videoName+filetype))
					os.remove(new_file)
				elif(VorA == 'v' or VorA == 'video'):
					add_video_thumbnail(item.thumbnail_url,destination,(videoName+filetype))
				tqdm.write("'" + videoName + filetype + "'" + " has been successfully downloaded.")
				download_counter += 1
			
		else:
			tqdm.write("'" + videoName + filetype + "'" " is already in the file.")
	else:
		print("This program can only download files with at least one ascii character in the name")
		name_error_counter += 1
	

	

print("\n")
print("DOWNLOAD COMPLETE!")
print(str(download_counter) + " files have been downloaded which means " + str(len(playlist.video_urls)-download_counter) + " out of " + str(len(playlist.video_urls)) + " files were downloaded prior to the script running")
print("There were " + str(error_counter) + " error(s) encountered")
if(name_error_counter >0):
	print("There were " + str(name_error_counter) + " file(s) with only non-ascii characters in the title")
input("Press any key to exit")