from pwn import * # pip3 install pwntools

conn = remote('ctf.k3rn3l4rmy.com', '2237')
l = [b'' for _ in range(10**4)]

def get_flag(conn, l):
	conn.sendline(b'2')
	conn.recvuntil(b': ')
	conn.sendline(b' '.join(l))
	print(conn.recvuntil(b'}'))

def get_num(conn, indexes):
	conn.sendline(b'1')
	conn.sendline(indexes.encode())
	p = conn.recvuntil(b'\n')[70:-2]
	return p.split(b', ')

def solve():
	for i in range(100):
		s = ''
		for j in range(100): 
			s += ' '.join(str(i*100 + j) for _ in range(j + 1)) + ' '
		ll = get_num(conn, s[:-1])
		d = {}
		for x in ll: d[ll.count(x)] = x
		for x in d:
			l[i*100 + x - 1] = d[x]
		print(l.count(b''))

solve()
get_flag(conn, l)