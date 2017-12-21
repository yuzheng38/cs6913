import pyjsonrpc

URL = 'http://localhost:6060/'
text = 'some random text... this should be low.'


test_client = pyjsonrpc.HttpClient(url=URL)
rel = test_client.call('classify', text)
print rel
