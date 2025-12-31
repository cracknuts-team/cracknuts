log = '''

'''

s = log.index('{"traceback": [')
e = log.index('], "ename":')
for line in log[s+15:e].split(', '):
    print(line)

