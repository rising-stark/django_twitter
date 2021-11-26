import re
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User, auth
from django.db.models import Sum
from tweet.models import *

def home(request):
	return render(request, "home.html")

def splash(request):
	return render(request, "home.html")

def login(request):
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']

		user = auth.authenticate(username=username,password=password)

		if user is not None:
			auth.login(request, user)
			return redirect("tweet")
		else:
			messages.info(request, 'invalid credentials')
			return render(request, 'login.html')

	# If user is already logged in then render the twitter feed
	if request.user.is_authenticated:
		return redirect('tweet')

	return render(request, 'login.html')

def signup(request):
	if request.method == 'POST':
		username = request.POST['username']
		email = request.POST['email']
		password = request.POST['password']
		confirm_password = request.POST['confirm_password']

		if password == confirm_password:
			if User.objects.get(username=username).exists():
				messages.info(request, 'Username Taken. Choose a differet username')
				return render(request, 'login.html')
			elif User.objects.get(email=email).exists():
				messages.info(request, 'An account with this email aready exists.')
				return render(request, 'login.html')
			else:
				user = User.objects.create_user(username=username, password=password, email=email)
				user.save();
				print('user created')
				auth.login(request, user)
				print('user automatically logged-in')
				return redirect('tweet')
		else:
			messages.info(request, 'passwords not matching...')
			return render(request, 'login.html')

	return redirect('login')

def logout(request):
	auth.logout(request)
	return redirect('/')


def tweet(request):
	if not request.user.is_authenticated:
		messages.info(request, 'You need to be logged-in to access twitter feed.')
		messages.info(request, 'Don\'t have an account yet? Signup now')
		return redirect('login')

	if request.method == "POST":
		tweet = request.POST["tweet"]
		print("user here  = ", request.user)
		t = Tweets(username = request.user, tweet = tweet)
		t.save()
		list = re.findall("[#]\w+", tweet)
		for hashtag in list:
			obj, created = Hashtag_tweets.objects.get_or_create(hashtag=hashtag[1:], tweet_id=t)
			obj.count += 1
			obj.save()

	hashtags = Hashtag_tweets.objects.values('hashtag').order_by('hashtag').annotate(count=Sum('count'))
	tweets = Tweets.objects.all().order_by('-date_created')
	print("\n\nhashtags = \n\n" , hashtags)
	print("\n\ntweets = \n\n" , tweets)
	return render(request, "tweet.html", {"hashtags" : hashtags, "tweets":tweets})

def like(request):
	if request.method == "POST":
		tweet_id = request.POST["tweet_id"]
		t = Tweets.objects.get(pk=tweet_id)
		obj, not_liked = Like_tweets.objects.get_or_create(username = request.user, tweet_id = t)
		if not_liked:
			t.likes += 1
		else:
			obj.delete()
			t.likes -= 1
		t.save()
	return redirect('tweet')

def delete(request):
	if request.method == "POST":
		tweet_id = request.POST["tweet_id"]
		t = Tweets.objects.get(pk=tweet_id)
		t.delete()
	return redirect('tweet')

def profile(request):
	if not request.user.is_authenticated:
		messages.info(request, 'You need to be logged-in to access profile page.')
		messages.info(request, 'Don\'t have an account yet? Signup now')
		return redirect('login')

	username = request.GET.get("username")
	print("username in profile = ", username)
	# If username is not passed as query parameter then showing own profile
	if not username:
		username = request.user
		print("we reached here = ", username)

	tweets = None
	user = User.objects.get(username=username)
	if not user:
		messages.info(request, 'No such user exists')
	else:
		tweets = Tweets.objects.filter(username=user)
		print("\n\nin profile tweets = \n\n" , tweets)

	return render(request, "profile.html", {"tweets":tweets})