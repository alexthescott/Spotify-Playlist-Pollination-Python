""" repeatKing.py Python3
Alexander Scott
July 2019
Built to observe track cross pollination across User's public Spotify playlists
"""

import sys
import spotipy
import spotipy.util as util
import matplotlib.pyplot as plt
import numpy as np
import json

# Dumb and ignorant global variables
seen = list()
playlistCount = list()
totalTrackCount = 0
repeatCount = [0]

# Quality of life improvements
arbitraryFilter = True

# To-Do Playlists, Sadboys, and every running playlist
filter_keywords = ["Junior", "Sophomore", "Freshman", "Young_Junior", "Young_Senior", "7-10 grade", "TheIndieBlog", "BPM"]

# My "archive time period" playlists
extraFilterList = []

class Playlist(object):
	def __init__(self, name, length):
		self.name = name
		self.count = 1
		self.length = length
		# Will be altered
		self.score = self.count / self.length

	def changeCount(self, count):
		self.count += 1 / count
		self.score = 100 * (self.count / self.length)

	def printSelf(self):
		print(str(round(self.score, 3)) + "% " + self.name)

# Define custom track object ---------------------------------------------------------------------
class Track(object):
	def __init__(self, artist, trackName, playlist):
		self.artist = artist
		self.trackName = trackName
		self.count = 1
		self.playlists = list()
		self.playlists.append(playlist)
		repeatCount[0] += 1

	def addPlaylist(self, playlist):
		repeatCount[self.count - 1] -= 1
		self.count += 1
		self.playlists.append(playlist)
		if len(repeatCount) < self.count:
			repeatCount.append(1)
		else:
			repeatCount[self.count - 1] += 1
		

	def printSelf(self):
		print("%d %s %s" % (self.count, self.artist, self.trackName))
		self.playlists.sort()
		for p in self.playlists:
			print(p + ",", end=' ')
		print("\n")

def checkPlaylistList(playlistName):
	for playlist in playlistCount:
		if playlist.name == playlistName:
			return playlistCount.index(playlist)
	return -1

def checkSeen(artist, trackName):
    for Track in seen:
                if Track.trackName == trackName and Track.artist == artist:
                        return seen.index(Track)
    return -1

def show_tracks(tracks, count, playlist):
        for item in tracks['items']:
                track = item['track']
                
                count += 1

                artist = track['artists'][0]['name']
                trackName = track['name']
                print("     %d %32.32s %s" % (count, artist, trackName))
                index = checkSeen(artist, trackName)
                if index != -1:
                	seen[index].addPlaylist(playlist)
                	seen.sort(key=lambda track: track.count, reverse = True)
                else:
                	seen.append(Track(artist, trackName, playlist))
                	seen.sort(key=lambda track: track.count, reverse = True)
        return count
# Create Spotify Object --------------------------------------------------------------------------



# Ask for Spotify Username 
username = raw_input('Enter Spotify Username:')
# username = ''

# Generate your own @ https://developer.spotify.com/dashboard/, set redirect to google url below
client_id = ''
client_secret = ''
redirect_uri = 'http://www.google.com/'

# Assign scope and creates token for Spotipy object
scope = "playlist-modify-public"
token = util.prompt_for_user_token(username, scope, client_id, client_secret, redirect_uri)

# Create Spotify Object
sp = spotipy.Spotify(auth=token)

# Create Playlist Object
playlists = sp.user_playlists(username)

# Main -------------------------------------------------------------------------------------------
while playlists:
	for pCount, playlist in enumerate(playlists['items']):
		if playlist['owner']['id'] == username:
			if arbitraryFilter and any(word in playlist['name'] for word in filter_keywords):
				break
			totalTrackCount += playlist['tracks']['total']
			playlistCount.append(Playlist(playlist['name'], playlist['tracks']['total']))
			currentCount = 1
			print(playlist['name'])
			print(' total tracks', playlist['tracks']['total'])
			results = sp.user_playlist(username, playlist['id'], fields="tracks,next")
			tracks = results['tracks']
			currentCount = show_tracks(tracks, currentCount, playlist['name'])
			while tracks['next']:
				tracks = sp.next(tracks)
				currentCount = show_tracks(tracks, currentCount, playlist['name'])
	if playlists['next']:
	    playlists = sp.next(playlists)
	else:
	    playlists = None

# CalculateValues
mean = totalTrackCount / len(seen)

seen.sort(key=lambda track: track.count, reverse = False)


for track in seen:
	for p in track.playlists:
		index = checkPlaylistList(p)
		playlistCount[index].changeCount(len(track.playlists))


# Mean and Filter Quality of life improvements
print("arbitraryFilter = " + str(arbitraryFilter))
print("\n" + "Mean playlists per track: " + str(round(mean, 4)) + "\n")
numberRepeatCount = list()
trackPercent = list()
for i, count in enumerate(repeatCount):
	percent = round(100 * (count / len(seen)), 2)
	trackPercent.append(percent)
	numberRepeatCount.append(i + 1)
	if i == 0: print("track in 1 playlist " + str(percent) + "%")
	else: print("track in " + str(i + 1) + " playlists " + str(percent) + "%")
print("\n")

# Collect and show Playlist Track Individuality Score
print("'score' of track individuality. Sum of 'track score' / playlist track count")
print("'track score' == 1 / n points for n playlist instances" + "\n")
playlistScores = list()
playlistNames = list()
playlistCount.sort(key=lambda playlist: playlist.score, reverse = True)
for p in playlistCount:
	p.printSelf()
	playlistScores.append(p.score)
	playlistNames.append(p.name)
	
print("\n" + "Worst Track Offenders ")
seen.sort(key=lambda track: track.count, reverse = True)
for i in range(0, 31):
	seen[i].printSelf()

""" Playlist Individuality Graph """
playlistIndex = np.arange(len(playlistCount))
plt.ylabel("Playlist Individuality Score")
plt.bar(playlistIndex, playlistScores)
plt.xticks(playlistIndex, playlistNames, rotation='vertical')
plt.axis('auto')
plt.grid(True)
plt.annotate("Score = (Sum of 1 / n) / trackCount, n = track's playlist instances", xy=(.3, .95), xycoords='axes fraction')
plt.yticks(np.arange(0, playlistScores[0], step = 10.0), rotation='vertical')
plt.show() 

""" Track Playlist Distribution Graph """
trackIndex = np.arange(len(repeatCount))
plt.ylabel("% of Distribution")
plt.xlabel("Number of playlists per track")
plt.bar(trackIndex, trackPercent)
plt.xticks(trackIndex, numberRepeatCount, rotation = 'vertical')
plt.axis('auto')
plt.grid(True)
plt.annotate("Mean playlist per track: " + str(round(mean, 4)), xy=(.5, .95), xycoords = 'axes fraction')
plt.yticks(np.arange(0, trackPercent[0], step = 10), rotation='vertical')
for i, v in enumerate(trackPercent):
	plt.text(trackIndex[i] - .3,trackPercent[i], trackPercent[i], size = 6)
plt.show()




