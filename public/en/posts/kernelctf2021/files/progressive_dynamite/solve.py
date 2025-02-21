from Crypto.Util.number import *

with open('challenge.txt') as f: l = eval(f.read())

dp = list([list([-1 for x in range(100)]) for x in range(100)])

def solve(l, i, j):
	if dp[i][j] != -1: return dp[i][j]
	if i == len(l) - 1:
		return sum(l[i][j:])
	if j == len(l) - 1:
		return sum(x[j] for x in l[i:])
	dp[i][j] = l[i][j] + min(solve(l, i+1, j), solve(l, i, j+1))
	return dp[i][j]

x = solve(l, 0, 0)
x -= 38396724472483865997960720090198028896
print('Flag:', long_to_bytes(x).decode())