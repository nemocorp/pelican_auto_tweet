# Pelican-Twitter Bridge

This set of Python scripts are aimed at allowing users of the [Pelican](http://getpelican.com) blog engine to link some of their posts to Twitter.

## Presentation

For now, I only wrote two scripts:

- `pelican_auto_tweet.py`
- `pelican_tweet_summary.py`

The first one is usefull to automatically post a tweet on Twitter for the latest blog post. As Pelican is text-based and often used with Git, this script makes use of Git logs to find new posts. More details are given below.

The second script posts a tweet on Twitter for each article posted on the blog in the last 7 days. Like the previous script, I give some details below.

## Installation

Just fork this repo! :)

Since I use two external libraries, you also need to install them if you want to use these scripts.

### Python-Twitter

Located at [http://code.google.com/p/python-twitter/](http://code.google.com/p/python-twitter/), the steps for installing it are : 

	hg clone http://python-twitter.googlecode.com/hg/ python-twitter
	cd python-twitter
	hg update
	python setup.py build
	python setup.py install

### Bitly 

To shorten links, I use Bitly. This API is available in Pypi repository, so installation is quite easy.

	pip install bitly_api

The results of requests made to Bitly API are Unicode encoded, so I also need a library to re-encode them. This library is [Unidecode](https://pypi.python.org/pypi/Unidecode). _If you have a better way to work with Bitly, I will appreciate if you can tell me about!_

	git clone http://www.tablix.org/~avian/git/unidecode.git unidecode
	python setup.py build
	python setup.py install

## Usage

The script need some configuration. For this, create the file `conf.py`.

	/
	|- conf.py
	|- pelican_auto_tweet.py
	|- pelican_tweet_summary.py
	|- README

In this script, you **have** to define four variables for the [Twitter API](https://dev.twitter.com) : 

	CONSUMER_KEY = ''
	CONSUMER_SECRET = ''
	ACCESS_TOKEN = ''
	ACCESS_TOKEN_SECRET = ''

Now, you can use the scripts.

### Pelican_auto_tweet

I use this script to tweet the link of my **last** blog post. 

I use Git to backup my blog. After each new blog post, I commit the new file with a commit message that starts with '[POST]'. I adapted the script to my own needs, so it get the last commit message, and if the message starts with '[POST]', it tweets it.

The tweet message is the title of the post (post variable `Title:`), followed by its URL. To construct the URL, the script extract the URL of the site in the `pelicanconf.py` file (variable `SITEURL=`), and append to it the slug of the blog post (variable `Slug:` in the header of the blog post file).

The tweet sent use the following format : 

> {{TITLE}} {{URL}} #blog

To launch the script, you have some options.

1. Run it directly from the root of your Pelican directory:
	```
	$ python ~/pelican_auto_tweet.py
	```
2. Run it from anywhere, and give it the path to the root of your Pelican directory:
	```
	$ python ~/pelican_auto_tweet.py ~/pelican_blog/
	```	

### Pelican_tweet_summary

This script sends one tweet for each blog post published in the last 7 days. Each tweet is sent 3 minutes after the previous one.

I use the same method I used for the previous script to get the URL of the posts, or their title.

The usage of this script is quite the same as the previous one

1. Run it directly from the root of your Pelican directory:
	```
	$ python ~/pelican_tweet_summary.py
	```
2. Run it from anywhere, and give it the path to the root of your Pelican directory:
	```
	$ python ~/pelican_tweet_summary.py ~/pelican_blog/
	```

## More

I wrote some posts on my blog about this script : 

- [Presentation](https://quack1.me/pelican_auto_tweet.html) ;
- [How to automate the publication with Git #TODO](https://quack1.me/).

I created the theme I use on my blog, which is available [on Github](https://github.com/quack1/notebook).