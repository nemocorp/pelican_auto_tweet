#! /usr/bin/env python
# -*- coding: utf-8 -*- #
# 
#            --------------------------------------------------
#                             Pelican_Auto_Tweet          
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
'''This script is used to automaticaly tweet link of the last published post from
a Pelican blog.
Both Markdown and Rest syntax are supported. The 'Slug' tag **have** to be set
	so the script can create the complete URI to the post.'''

__author__ = 'quack1'
__version = '0.1'
#	**About Author** :
#    
#	Founder : Quack1
#	Location : Paris - France
#	Email : quack+pelican_auto_tweet@quack1.me
#	 
#	Project In GitHub : https://github.com/quack1/pelican_auto_tweet
#	Blog : https://quack1.me
#
import re
import os.path
import sys
import commands
import os
# From https://github.com/bitly/bitly-api-python
import bitly_api as bitlyapi
# From http://code.google.com/p/python-twitter/
import twitter
import unicodedata

from conf import *

BASE_DIR = ''
SITE_BASE_URL = ''
REGEX_BASE_URL = re.compile(r'SITEURL = \'(.*)\'',re.IGNORECASE)
REGEX_TITLE = re.compile(r'Title:\s+(.*)',re.IGNORECASE)
REGEX_SLUG = re.compile(r'Slug:\s+(.*)',re.IGNORECASE)
TWITTER_API = None
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
	with open(os.path.join(BASE_DIR, filename),"r") as f:
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

# Check arguments
if len(sys.argv) >= 2:
	BASE_DIR = sys.argv[1]
elif not BASE_DIR:
	BASE_DIR = './'


if not BASE_DIR:
	print 'Error... No content dir'
	sys.exit(2)

BITLY_API = bitlyapi.Connection(BITLY_USER, BITLY_API_KEY)

get_site_base_url()
if not SITE_BASE_URL.endswith('/') : 
	SITE_BASE_URL = SITE_BASE_URL + '/'

os.chdir(BASE_DIR)
result = commands.getoutput('git show --pretty="format:%s" --name-only')

log_message = result.splitlines()[0]
files = result.splitlines()[1:]

if log_message.startswith('[POST]'):
	os.system('git push')
	os.system('make ssh_upload')
	for filename in files:
		base, ext = os.path.splitext(filename)
		if base.startswith('content/') and ext in ('.rst','.md'):
			title,slug = get_post_infos(os.path.join(BASE_DIR, filename))
			url = SITE_BASE_URL + slug + ".html"
			s = BITLY_API.shorten(url)
			u = s['url']
			url = unicodedata.normalize('NFKD', u).encode('ascii','ignore')
			tweet_text = "%s %s #blog"%(title,url)
			twitter_send(tweet_text)
sys.exit(0)
