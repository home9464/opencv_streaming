from modem import Modem
m = Modem()
m.connect('fast.t-mobile.com')
#m.http_request('http://www.google.com')
#m.disconnect()
print(m.get_ip_addr())
#print(m.get_signal_strength())
