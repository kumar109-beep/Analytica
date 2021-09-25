from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.views.decorators.csrf import csrf_exempt

from django.shortcuts import redirect

from django.contrib.auth import authenticate, login

import requests, json

from django.contrib.auth.forms import AuthenticationForm
from .forms import RegistrationForm

from rolepermissions.roles import assign_role

from rolepermissions.checkers import has_role
from analytica.roles import NHPUser, Admin, Member, Contributor

def index(request):
	signinform = AuthenticationForm()
	signupform = RegistrationForm()
	template = loader.get_template('home/index.html')
	context = {}
	if not request.user.is_authenticated:
		context = {
			'signinform': signinform,
			'signupform':signupform
		}
	return HttpResponse(template.render(context, request))

def about(request):
	template = loader.get_template('home/about.html')
	context = {'latest_question_list': "",}
	return HttpResponse(template.render(context, request))

def contact(request):
	template = loader.get_template('home/contact.html')
	context = {'latest_question_list': "",}
	return HttpResponse(template.render(context, request))

def faq(request):
	template = loader.get_template('home/faq.html')
	context = {'latest_question_list': "",}
	return HttpResponse(template.render(context, request))


@csrf_exempt
def bcpm_login(request):
	headers = {'User-Agent': 'Mozilla/5.0'}
	payload = {'user_id':request.POST.get('user_id') ,'pass':request.POST.get('pass')}
	session = requests.Session()
	response = session.post('http://nhm-bcpm.in/nhm/login_dashboard.php',headers=headers,data=payload)
	if(response.content == b'{"status":1,"message":"Successful","error":""}'):
		user = authenticate(username = "tattva", password = "Welcome!1")
		if user is not None:
			login(request, user)
		return redirect('analytics', profile="asha")
	else:
		# template = loader.get_template('registration/login.html')
		# context = {'invalid': True,}
		# return HttpResponse(template.render(context, request))
		return redirect('login')

	# return HttpResponse(response, content_type="application/json")

def loginView(request):
	if request.method == 'POST':
		form = AuthenticationForm(data=request.POST)
		if form.is_valid():
			user = form.get_user()
			login(request, user)
			return redirect('/website/profile/')
	else:
		form = AuthenticationForm()
	return render(request, 'website/login.html', {'form': form})


def loginUser(request):
	username= request.POST.get('username')
	password = request.POST.get('password')
	stayloggedin = request.GET.get('stayloggedin')
	if stayloggedin:
		request.session.set_expiry(0)

	user = authenticate(username=username, password=password)
	if user is not None:
		if user.is_active:
			login(request, user)	
			if has_role(user, [Admin, Member, Contributor]):
				profile = "asha"
			elif has_role(user, [NHPUser]):
				profile = "committee"
			else:
				profile = False
			return HttpResponse(json.dumps({"user": user.username, "status":"active", "profile":profile}),content_type="application/json")
		else:
			return HttpResponse(json.dumps({"user": user.username, "status": "inactive"}), content_type="application/json")
	else:
		return HttpResponse(json.dumps({"status": "invalid"}),content_type="application/json")
	return HttpResponse(json.dumps({"status": "denied"}),content_type="application/json")

def signup(request):
	if request.user.is_authenticated:
		return redirect('/')
	if request.method == 'POST':
		username = request.POST.get('username')
		fname = request.POST.get('first_name')
		lname = request.POST.get('last_name')
		email = request.POST.get('email')
		password1 = request.POST.get('password1')
		password2 = request.POST.get('password2')
		data = {'username':username, 'first_name':fname, 'last_name':lname, 'email':email, 'password2':password2, 'password1':password1}
		form = RegistrationForm(data = data)
		if form.is_valid():
			user = form.save(commit=False)
			user.is_active = True
			user.save()
			assign_role(user, "guest")
			return HttpResponse(json.dumps({"status": "Success"}),content_type="application/json")
		else:
			return HttpResponse(json.dumps({"status":"Error", "error":form.errors}),content_type="application/json")
	else:
		# form = RegistrationForm()
		pass
	return HttpResponse(json.dumps({"status": "Denied"}),content_type="application/json")


def default_page(requests):
	print("dansih")
	return HttpResponseRedirect('/')