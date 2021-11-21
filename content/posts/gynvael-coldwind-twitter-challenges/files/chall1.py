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