+++
title = "Gynvael Coldwind Twitter Challenges"
description = "Solved some nodejs twitter challenges posted by Gynvael coldwind on twitter"
date = 2020-08-27T08:59:32+05:30
featured = false
draft = false
comment = false
toc = true
reward = false
categories = [
  "twitter challenge"
]
tags = [
  "twitter",
  "challenge",
  "writeups",
  "web"
]
series = []
images = ["images/gynvael_bg_logo.jpeg"]
+++

Scrolling through the twitter, I found a series of nodejs challenges posted by [@gynvael](https://twitter.com/gynvael). I gave it a try and solved 3 out of 5 challenges!  

Here are the writeups for the challenges I have solved...

<!--more-->

## Challenge 1
**Challenge URL:** [http://35.204.139.205:5000/](http://35.204.139.205:5000/)  
**Source code:** [source.py](files/chall1.py)
```py3
#!/usr/bin/python3
from flask import Flask, request, Response, render_template_string
from urllib.parse import urlparse
import socket
import os

app = Flask(__name__)
FLAG = os.environ.get('FLAG', "???")

with open("task.py") as f:
	SOURCE = f.read()

@app.route('/secret')
def secret():
	if request.remote_addr != "127.0.0.1":
		return "Access denied!"

	if request.headers.get("X-Secret", "") != "YEAH":
		return "Nope."

	return f"GOOD WORK! Flag is {FLAG}"

@app.route('/')
def index():
	return render_template_string(
			"""
			&lt;html&gt;
				&lt;body&gt;
					&lt;h1&gt;URL proxy with language preference!&lt;/h1&gt;
					&lt;form action="/fetch" method="POST"&gt;
						&lt;p&gt;URL: &lt;input name="url" value="http://gynvael.coldwind.pl/"&gt;&lt;/p&gt;
						&lt;p&gt;Language code: &lt;input name="lang" value="en-US"&gt;&lt;/p&gt;
						&lt;p&gt;&lt;input type="submit"&gt;&lt;/p&gt;
					&lt;/form&gt;
					&lt;pre&gt;
Task source:
{{ src }}
					&lt;/pre&gt;
				&lt;/body&gt;
			&lt;/html&gt;
			""", src=SOURCE)

@app.route('/fetch', methods=["POST"])
def fetch():
	url = request.form.get("url", "")
	lang = request.form.get("lang", "en-US")

	if not url:
		return "URL must be provided"

	data = fetch_url(url, lang)
	if data is None:
		return "Failed."

	return Response(data, mimetype="text/plain;charset=utf-8")

def fetch_url(url, lang):
	o = urlparse(url)

	req = '\r\n'.join([
		f"GET {o.path} HTTP/1.1",
		f"Host: {o.netloc}",
		f"Connection: close",
		f"Accept-Language: {lang}",
		"",
		""
	])

	res = o.netloc.split(':')
	if len(res) == 1:
		host = res[0]
		port = 80
	else:
		host = res[0]
		port = int(res[1])

	data = b""
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		s.connect((host, port))
		s.sendall(req.encode('utf-8'))
		while True:
			data_part = s.recv(1024)
			if not data_part:
				break
			data += data_part

	return data

if __name__ == "__main__":
	app.run(debug=False, host="0.0.0.0")
```
> **Solution**
> 
> **cURL command:** curl -XPOST 'http://35.204.139.205:5000/fetch' --data-raw 'url=http://localhost:5000/secret&lang=XX%0D%0AX-Secret:%20YEAH'
>
> **Explanation**
> 
> The lang parameter is not whitelisted and is passed directly into the headers of request. So we can insert a CRLF and required header (X-Secret) with value YEAH and send the request to localhost:5000/secret asking for flag!

---

## Challenge 2
**Challenge URL:** [http://challenges.gynvael.stream:5002/](http://challenges.gynvael.stream:5002/)  
**Source code:** [source.js](files/chall2.js)
```js
const express = require("express");
const fs = require("fs");

const PORT = 5002;
const FLAG = process.env.FLAG || "???";
const SOURCE = fs.readFileSync("app.js");

const app = express();

app.get("/", (req, res) => {
	res.statusCode = 200;
	res.setHeader("Content-Type", "text/plain;charset=utf-8");
	res.write("Level 2\n\n");

	if (!("X" in req.query)) {
		res.end(SOURCE);
		return;
	}

	if (req.query.X.length > 800) {
		const s = JSON.stringify(req.query.X);
		if (s.length > 100) {
			res.end("Go away.");
			return;
		}

		try {
			const k = "&lt;" + req.query.X + "&gt;";
			res.end("Close, but no cigar.");
		} catch {
			res.end(FLAG);
		}
	} else {
		res.end("No way.");
		return;
	}
});

app.listen(PORT, () => {
	console.log(`Challenge listening at port ${PORT}`);
});
```
> **Solution**
> 
> **cURL command:** curl 'http://challenges.gynvael.stream:5002/?X[length]=801&X[toString]=1'
>
> **Explanation**
> 
> Here the param X can be an object by sending get param as X[key]=value and this leads to prototype pollution. To satisfy the given conditions, we have to set X[length] > 800 and X[toString] property to some value. Because in JS while concatenating an object with a string, the toString method is called and if we change it's value, it raises an error and gives the flag!

---

## Challenge 4
**Challenge URL:** [http://challenges.gynvael.stream:5004/](http://challenges.gynvael.stream:5004/)  
**Source code:** [source.js](files/chall4.js)
```js
const express = require('express')
const fs = require('fs')
const path = require('path')

const PORT = 5004
const FLAG = process.env.FLAG || "???"
const SOURCE = fs.readFileSync(path.basename(__filename))

const app = express()

app.use(express.text({
	verify: (req, res, body) => {
		const magic = Buffer.from('ShowMeTheFlag')

		if (body.includes(magic)) {
			throw new Error("Go away.")
		}
	}
}))

app.post('/flag', (req, res) => {
	res.statusCode = 200
	res.setHeader('Content-Type', 'text/plain;charset=utf-8')
	if ((typeof req.body) !== 'string') {
		res.end("What?")
		return
	}

	if (req.body.includes('ShowMeTheFlag')) {
		res.end(FLAG)
		return
	}

	res.end("Say the magic phrase!")
})

app.get('/', (req, res) => {
	res.statusCode = 200
	res.setHeader('Content-Type', 'text/plain;charset=utf-8')
	res.write("Level 4\n\n")
	res.end(SOURCE)
})

app.listen(PORT, () => {
	console.log(`Challenge listening at port ${PORT}`)
})
```
> **Solution**
> 
> **cURL command:** echo -e "\x00S\x00h\x00o\x00w\x00M\x00e\x00T\x00h\x00e\x00F\x00l\x00a\x00g" | curl -XPOST 'http://challenges.gynvael.stream:5004/flag' --data-binary @- -H 'Content-Type: text/plain;charset=UTF-16'
>
> **Explanation**
>
> First things first, points to note:
> 1. Using express.text to parse the request body.
> 2. typeof req.body should be string.
> 
> I googled about the express.text and landed on [this](https://expressjs.com/en/api.html#express.text) page. So as mentioned in that page, the express.text triggers only when the content-type is text/plain (or other text types). And also this makes sense, because if we send content-type as text/plain, the typeof req.body will be a string, as mentioned in the 2nd point. Now the only difference between body send to express.text and req.body is, the raw data of request is used in express.text and parsed data (if encoded) is given to req.body. Now we can send the required data (ShowMeTheFlag) encoded as UTF-16 and specifying it in the content-type header and we get the flag!

I am not able to solve the other 2 challs. For their solutions refer to this [link](https://oshogbo.vexillium.org/).

---

##### Thanks for reading! {align=center}