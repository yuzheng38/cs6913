import pyjsonrpc

URL = 'http://localhost:6060/'
text = 'Trump worst president in US history'


test_client = pyjsonrpc.HttpClient(url=URL)
rel = test_client.call('classify', text)
print rel
