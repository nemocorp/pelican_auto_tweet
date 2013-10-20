#! /usr/bin/env python
# -*- coding: utf-8 -*- #
# 
#            --------------------------------------------------
#                             Pelican_Tweet_Summary          
#            --------------------------------------------------
#		Copyright (c) 2013, Quack1
#		All rights reserved.
#		Redistribution and use in source and binary forms, with or without
#		modification, are permitted provided that the following conditions are met:
#
#		* Redistributions of source code must retain the above copyright
#		  notice, this list of conditions and the following disclaimer.
#		* Redistributions in binary form must reproduce the above copyright
#		  notice, this list of conditions and the following disclaimer in the
#		  documentation and/or other materials provided with the distribution.
#		* Neither the name of Quack1 nor the
#		  names of its contributors may be used to endorse or promote products
#		  derived from this software without specific prior written permission.
#
#		THIS SOFTWARE IS PROVIDED BY QUACK1 "AS IS" AND ANY
#		EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#		WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#		DISCLAIMED. IN NO EVENT SHALL QUACK1 BE LIABLE FOR ANY
#		DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#		(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#		LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#		ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#		(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#		SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#
#
'''This script is used to automaticaly tweet links to the blog posts published in the
	last 7 days on the blog.
Both Markdown and Rest syntax are supported. The 'Slug' tag **have** to be set
	so the script can create the complete URI to the post.'''

__author__ = 'quack1'
__version = '0.3'
#	**About Author** :
#    
#	Founder : Quack1
#	Location : Paris - France
#	Email : quack1blog@gmail.com
#	 
#	Project In GitHub : https://github.com/quack1/pelican_auto_tweet
#	Blog : https://quack1.me
#
#	History:
#	  - 0.1
#		- Publish tweets, one every 3 minutes
#	  - 0.2
#		- Add support of Bitly
#	  - 0.3
#		- Make use of Bitly optional.
#		  If the script cannot connect to Bitly API, the url of the blog posts
#		  are sent as they are displayed in browser.

import datetime
import os
import re
import sys
import time
import twitter
import bitly_api as bitlyapi
import unicodedata
from conf import *


REGEX_DATE = re.compile(r'date: (\d{4})-(\d{2})-(\d{2}) \d{2}:\d{2}',re.IGNORECASE)
REGEX_BASE_URL = re.compile(r'SITEURL = \'(.*)\'',re.IGNORECASE)
REGEX_TITLE = re.compile(r'Title:\s+(.*)',re.IGNORECASE)
REGEX_SLUG = re.compile(r'Slug:\s+(.*)',re.IGNORECASE)
TODAY = datetime.date.today()
SITE_BASE_URL = ''
TWITTER_API = None
FIRST_TWEETED = False
SLUGS = []
DATES = []
TITLES = []
BITLY_API = None

def twitter_connect():
	'''Connect the API to Twitter with the OAuth protocol.'''
	global TWITTER_API
	TWITTER_API = twitter.Api(consumer_key=CONSUMER_KEY, 
		consumer_secret=CONSUMER_SECRET, access_token_key=ACCESS_TOKEN, 
    access_token_secret=ACCESS_TOKEN_SECRET)

def twitter_send(text):
	'''Post an update on Twitter.
	If the API is not connected, a call to twitter_connect() is made.'''
	if not TWITTER_API:
		twitter_connect()
	TWITTER_API.PostUpdate(text)
	print(text)

def get_site_base_url():
	'''Get the site base url from the pelicanconf.py file.
	The file must be located at ../pelicanconf.py related to the base 
	directory given in the parameter of the script'''
	global SITE_BASE_URL
	f = open(os.path.join(BASE_DIR,"pelicanconf.py"))
	if f:
		for l in f:
			res = REGEX_BASE_URL.search(l)
			if res:
				SITE_BASE_URL = res.group(1)
				if not SITE_BASE_URL.endswith('/'):
					SITE_BASE_URL += '/'
				break
		f.close()

def get_post_infos(filename):
	'''Get the base informations necessary to build the text send 
	to Twitter from the post source file. The 2 read tags are 'title'
	and 'slug'.'''
	title,url = '',''
	with open(filename,"r") as f:
		for line in f:
				res = REGEX_TITLE.search(line)
				if res:
					title = res.group(1)
				else:
					res = REGEX_SLUG.search(line)
					if res:
						url = res.group(1)
	if not url:
		url = ''
	return title,url

def first_tweet():
	global FIRST_TWEETED
	global SITE_BASE_URL
	if not FIRST_TWEETED:
		msg = '#blogReplay Voici les articles publiés ces 7 derniers jours sur %s'%SITE_BASE_URL
		twitter_send(msg)
		FIRST_TWEETED = True

# Check arguments
if len(sys.argv) >= 2:
	BASE_DIR = sys.argv[1]
elif not BASE_DIR:
	BASE_DIR = './'

if not BASE_DIR:
	print 'Error... No content dir'
	sys.exit(2)


get_site_base_url()

# Trying to connect to BitlyAPI
try:
	if not BITLY_USER:
		print("Error. No BITLY_USER defined.")
	if not BITLY_API_KEY:
		print("Error. No BITLY_API_KEY defined.")
	BITLY_API = bitlyapi.Connection(BITLY_USER, BITLY_API_KEY)
except:
	BITLY_API = None

CONTENT_DIR = os.path.join(BASE_DIR,'content/')
for filename in os.listdir(CONTENT_DIR):
	base, ext = os.path.splitext(filename)
	if ext in ('.rst','.md'):
		with open(os.path.join(CONTENT_DIR, filename),"r") as f:
			for line in f:
				res = REGEX_DATE.search(line)
				if res:
					year,month,day = int(res.group(1)),int(res.group(2)),int(res.group(3))
					post_date = datetime.date(year,month,day)
					if post_date+datetime.timedelta(7) >= TODAY:
						title,slug = get_post_infos(os.path.join(CONTENT_DIR, filename))
						if not slug in SLUGS:
							SLUGS.append(slug)
							DATES.append(post_date)
							TITLES.append(title)

if SITE_BASE_URL.endswith('/') : 
	SITE_BASE_URL = SITE_BASE_URL 
else:
	SITE_BASE_URL = SITE_BASE_URL + '/'

if len(SLUGS):
	POSTS = []
	for i in xrange(len(SLUGS)):
		article = {'slug':SLUGS[i],'date':DATES[i],'title':TITLES[i]}
		POSTS.append(article)
	POSTS.sort(key=lambda item:item['date'])
	
	first_tweet()
	for a in POSTS:
    	# Wait 3 miutes between 2 publications
		time.sleep(180)
		url = SITE_BASE_URL + a['slug'] + ".html"
		if BITLY_API:
			s = BITLY_API.shorten(url)
			u = s['url']
			url = unicodedata.normalize('NFKD', u).encode('ascii','ignore')
		title = a['title']
		max_length = 140 - len("#blogReplay ") - len(" #blog") - 5 - len(url)
		if len(title) >= max_length:
			title = "%s%s"%(title[:max_length],"...")
		tweet_text = "#blogReplay %s %s #blog"%(title,url)
		twitter_send(tweet_text)
	if len(SLUGS) == 1:
		twitter_send("C'était le seul article publié cette semaine. Fin du spam! :)")
	else:	
		twitter_send("C'était les %d articles publiés cette semaine. Fin du spam! :)"%len(SLUGS))
else:
	print("No new posts")

sys.exit(0)
