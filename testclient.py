from urllib import request

response = request.urlopen('http://localhost:8080/')
print('RESPONSE:\t', response)
print('URL:\t', response.geturl())

headers = response.info()
print('DATA:\t', headers['data'])
print('HEADERS:\t')
print('------------')
print('headers')

data = response.read().decode('utf-8')
print('LENGTH:\t', len(data))
print('DATA:\t')
print('------------')
print(data)

print('<Enter key> to exit...')
input()


