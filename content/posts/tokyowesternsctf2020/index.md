+++
title = "TokyoWesterns CTF 2020 Writeup [urlcheck V1&V2]"
description = "TokyoWesterns CTF -> Urlcheck v1 & v2 writeup"
date = 2020-09-20T08:59:00+05:30
featured = false
draft = false
comment = false
toc = true
reward = false
categories = [
  "ctf"
]
tags = [
  "ctfs",
  "writeups",
  "web"
]
series = []
images = ["images/tokyow_logo.png"]
+++

I have played [TokyoWesterns CTF 2020](https://ctftime.org/event/1086) with team [Invaders](https://ctftime.org/team/71588). We ended up at #21 worldwide.  
I solved only 2 web challenges -- Urlcheck v1 and Urlcheck v2. Should try harder next time!

<!--more-->

## Urlcheck v1
Given [server.py](files/server1.py)
```py3
import re, requests, flask
from urllib.parse import urlparse

app = flask.Flask(__name__)
app.flag = '***CENSORED***'
app.re_ip = re.compile('\A(\d+)\.(\d+)\.(\d+)\.(\d+)\Z')

def valid_ip(ip):
    matches = app.re_ip.match(ip)
	if matches == None:
		return False

	ip = list(map(int, matches.groups()))
	if any(i > 255 for i in ip) == True:
		return False
	# Stay out of my private!
	if ip[0] in [0, 10, 127] \
		or (ip[0] == 172 and (ip[1] > 15 or ip[1] < 32)) \
		or (ip[0] == 169 and ip[1] == 254) \
		or (ip[0] == 192 and ip[1] == 168):
		return False
	return True

def get(url, recursive_count=0):
	r = requests.get(url, allow_redirects=False)
	if 'location' in r.headers:
		if recursive_count > 2:
			return '&#x1f914;'
		url = r.headers.get('location')
		if valid_ip(urlparse(url).netloc) == False:
			return '&#x1f914;'
		return get(url, recursive_count + 1) 
	return r.text

@app.route('/admin-status')
def admin_status():
	if flask.request.remote_addr != '127.0.0.1':
		return '&#x1f97a;'
	return app.flag

@app.route('/check-status')
def check_status():
	url = flask.request.args.get('url', '')
	if valid_ip(urlparse(url).netloc) == False:
		return '&#x1f97a;'
	return get(url)

@app.route('/')
def index():
	return '''
<!DOCTYPE html>
<html>
<head>
  <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css">
  <script src="https://cdn.jsdelivr.net/npm/vue"></script>
</head>
<body>
	<div id="app" class="container">
	  <h1>urlcheck v1</h1>
	  <div class="input-group input-group-lg mb-3">
		<input v-model="url" placeholder="e.g.) http://11.45.148.93/" class="form-control">
		<div class="input-group-append">
		  <button v-on:click="checkStatus" class="btn btn-primary">check</button>
		</div>
	  </div>
	  <div v-if="status" class="alert alert-info">{{ d(status) }}</div>
	</div>
	<script>
	  new Vue({
		el: '#app',
		data: {url: '', status: ''},
		methods: {
		  d: function (s) {
			let t = document.createElement('textarea')
			t.innerHTML = s
			return t.value
		  },
		  checkStatus: function () {
			fetch('/check-status?url=' + this.url)
			  .then((r) => r.text())
			  .then((r) => {
				this.status = r
			  })
		  }
		}
	  })
	</script>
</body>
</html>
'''
```
The challenge is to bypass the valid_ip() function check using octal notation of ips.
> **Solution**
> 1. Our input url is passed to urlparse(url).netloc funtion which returns the part of url after '(schema:)//' and before the path part, which is basically the domain.
> 2. Then it is passed to the valid_ip(ip) function which checks the ip with given regex (like <num>.<num>.<num>.<num>) and then the ip is split into 4 parts for which the parts of ip are again checked with some given values to avoid some obvious SSRFs!
> 3. If all the checks were passed, the server will request that url, and inorder to get the flag we have to make the request to the localhost(127.0.0.1) /admin-status.
> 4. Now we can use the octal notation (0177.0.0.1) of IPs to bypass the valid_ip(ip) function check and send request to the localhost (127.0.0.1)
> 5. This obeys the regex and after split and converted to list it becomes [177,0,0,1] which passes the if condition checks too and when the server requests for the url, the octal notations is converted to normal ip (0177 -> 127) and 127.0.0.1/admin-status is requested and we get the flag!

Payload: [http://urlcheck1.chal.ctf.westerns.tokyo/check-status?url=http://0177.0.0.1/admin-status](http://urlcheck1.chal.ctf.westerns.tokyo/check-status?url=http://0177.0.0.1/admin-status)

---

## Urlcheck v2
Given [server.py](files/server2.py)
```py3
import ipaddress, socket, requests, flask
from urllib.parse import urlparse

app = flask.Flask(__name__)
app.flag = '***CENSORED***'

def valid_ip(ip):
	try:
		result = ipaddress.ip_address(ip)
		# Stay out of my private!
		return result.is_global
	except:
		return False

def valid_fqdn(fqdn):
	return valid_ip(socket.gethostbyname(fqdn))

def get(url, recursive_count=0):
	r = requests.get(url, allow_redirects=False)
	if 'location' in r.headers:
		if recursive_count > 2:
			return '&#x1f914;'
		url = r.headers.get('location')
		if valid_fqdn(urlparse(url).netloc) == False:
			return '&#x1f914;'
		return get(url, recursive_count + 1)
	return r.text

@app.route('/admin-status')
def admin_status():
	print('Remote Address:', flask.request.remote_addr)
	if flask.request.remote_addr != '127.0.0.1':
		return '&#x1f97a;'
	return app.flag

@app.route('/check-status')
def check_status():
	url = flask.request.args.get('url', '')
	if valid_fqdn(urlparse(url).netloc) == False:
		return '&#x1f97a;'
	return get(url)

@app.route('/')
def index():
	return '''
<!DOCTYPE html>
<html>
<head>
  <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css">
  <script src="https://cdn.jsdelivr.net/npm/vue"></script>
</head>
<body>
	<div id="app" class="container">
	  <h1>urlcheck v2</h1>
	  <div class="input-group input-group-lg mb-3">
		<input v-model="url" placeholder="e.g.) http://westerns.tokyo/" class="form-control">
		<div class="input-group-append">
		  <button v-on:click="checkStatus" class="btn btn-primary">check</button>
		</div>
	  </div>
	  <div v-if="status" class="alert alert-info">{{ d(status) }}</div>
	</div>
	<script>
	  new Vue({
		el: '#app',
		data: {url: '', status: ''},
		methods: {
		  d: function (s) {
			let t = document.createElement('textarea')
			t.innerHTML = s
			return t.value
		  },
		  checkStatus: function () {
			fetch('/check-status?url=' + this.url)
			  .then((r) => r.text())
			  .then((r) => {
				this.status = r
			  })
		  }
		}
	  })
	</script>
</body>
</html>
'''
```
The challenge is to bypass the valid_fqdn() function check using DNS rebinding attack.
> **Solution**
> 1. Our input url is passed to urlparse(url).netloc funtion which returns the domain part in the url.
> 2. Then it is passed to the valid_fqdn(fqdn) function which gets the ip of the domain using socket.gethostbyname(host) function.
> 3. The ip is the passed to valid_ip(ip) function which uses the ipaddress module to determine whether the given ip is global or private. Only global ips are allowed!
> 4. If all the checks were passed, the server will request that url and we have to make the server request to the localhost(127.0.0.1) /admin-status to get the flag which is obviously a private url.
> 5. Here the DNS rebind attack comes into play! I noticed the import of time module, though there is no use of it in the code and this attack vector came to my mind.
> 6. As it is already implemented [here](https://lock.cmpxchg8b.com/rebinder.html), I just gave one ip as 127.0.0.1 and another public ip and sent the given url to the server.
> 7. The underlying concept of the DNS rebinding technique is to change the ip mapped to a domain in dns rapidly between a certain ips with 0 TTL (Time To Live), i.e., no dns cache, so that we get different ips for different dns requests. Using this we might get the host ip as public address in valid_fqdn check and when the request is made by the server we might get localhost ip. Since, it is not much reliable, we will send a series of requests, so that some might go exactly as planned, giving us the flag!

Payload: [http://urlcheck2.chal.ctf.westerns.tokyo/check-status?url=http://\<rand\>.\<rand\>.rbndr.us/admin-status](http://urlcheck2.chal.ctf.westerns.tokyo/check-status?url=http://<rand>.<rand>.rbndr.us/admin-status)

---

##### Thanks for reading! {align=center}