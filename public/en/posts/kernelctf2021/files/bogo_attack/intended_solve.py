from pwn import * # pip3 install pwntools

conn = remote('ctf.k3rn3l4rmy.com', '2247')
SIZE = 10**4
l = [b'' for _ in range(SIZE)]

def get_flag(conn, nums):
	conn.sendline(b'2')
	conn.sendline(nums.encode())
	print(conn.recvuntil(b'\n'))

def get_num(conn, indexes):
	conn.sendline(b'1')
	conn.sendline(indexes.encode())
	p = conn.recvuntil(b'\n')[70:-2]
	return set(int(x.decode()) for x in p.split(b', '))

def gen_str(int_list):
	return ' '.join(str(x) for x in int_list)

def complement(s):
	return set(range(SIZE)) - s

def solve():
	indexes_list = []
	nums_sets = []
	for i in range(15):
		tmp = set()
		for x in range(2**14):
			if x >= SIZE: continue
			x = list(bin(x)[2:].rjust(15, '0'))
			x[i] = '0'
			tmp.add(int(''.join(x), 2))
		indexes_list.append(list(tmp))
	for i in range(15):
		nums_sets.append(get_num(conn, gen_str(indexes_list[i])))
	for i in range(SIZE):
		x = bin(i)[2:].rjust(15, '0')
		num = set(range(SIZE))
		for index, k in enumerate(x):
			if k == '0':
				num = num.intersection(nums_sets[index])
			else:
				num = num.intersection(complement(nums_sets[index]))
		if i % 1000 == 0: print(i)
		l[i] = num.pop()

solve()
print('Getting flag...')
get_flag(conn, gen_str(l))