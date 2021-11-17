from pwn import * # pip3 install pwntools

conn = remote('ctf.k3rn3l4rmy.com', '2247')
l = [b'' for _ in range(10**4)] + [0]*100

def get_flag(conn, l):
	conn.sendline(b'2')
	conn.recvuntil(b': ')
	conn.sendline(b' '.join(l))
	print(conn.recvuntil(b'\n'))

def get_num(conn, indexes):
	conn.sendline(b'1')
	conn.sendline(indexes.encode())
	p = conn.recvuntil(b'\n')[70:-2]
	return p.split(b', ')

def gen_str(int_list):
	return ' '.join(str(x) for x in int_list)

def solve(): # xx * yy <= 10**4
	yy = 14
	even_list = get_num(conn, gen_str(list(range(10**4))[::2]))
	for i in range(yy):
		s = ''
		xx = 716
		for j in range(xx):
			mm = i*xx + j
			if mm >= 10**4: continue
			s += (str(mm) + ' ') * ((j // 2) + 1)
		ll = get_num(conn, s[:-1])
		d = {}
		for x in set(ll):
			key = ll.count(x)
			if key in d: d[key].append(x)
			else: d[key] = [x]

		for x in d:
			if d[x][0] in even_list:
				even = d[x][0]; odd = d[x][1]
			else:
				even = d[x][1]; odd = d[x][0]
			even_index = i*xx + 2*(x - 1)
			l[even_index] = even
			l[even_index + 1] = odd
		print(l.count(b''))

solve()
print('Getting flag...')
l = l[:10**4]
get_flag(conn, l)