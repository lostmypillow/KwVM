import proxmoxer
from pprint import pprint
host = "192.168.2.13"
username = "lostmypillow"
token_name = "lostmypillow"
x = proxmoxer.ProxmoxAPI(
						host,
						user=f"{username}@pve",
						token_name=token_name,
						token_value="245a4a7a-581f-434d-be48-e393d9578aa0",
						verify_ssl=False, 
						port=8006
					)
nodes = []
# ['pve1', 'pve2', 'pve3']
for node in x.cluster.resources.get(type='node'):
			if node['status'] == 'online':
				nodes.append(node['node'])


#x.cluster.resources.get(type='vm')
# all_vms = [{'cpu': 0.0132651315238784,
#   'disk': 0,
#   'diskread': 1368367616,
#   'diskwrite': 192353792,
#   'id': 'qemu/301',
#   'maxcpu': 2,
#   'maxdisk': 68719476736,
#   'maxmem': 2147483648,
#   'mem': 1216311296,
#   'name': 'Win10-01',
#   'netin': 5485099,
#   'netout': 124953,
#   'node': 'pve1',
#   'status': 'running',
#   'template': 0,
#   'type': 'qemu',
#   'uptime': 3430,
#   'vmid': 301}]		


# x.nodes('pve1').qemu('301').status.get('current')['status']
# 'running'
# pprint()

spiceconfig = x.nodes('pve1').qemu('301').spiceproxy.post()
y = '\n'.join(f"{k} = {v}" for k, v in spiceconfig.items())
print(y)
# for key, value in spiceconfig.items():
# 		if key == 'proxy':
# 			val = value[7:].lower()
# 			if val in G.spiceproxy_conv:
# 				print(f'http://{G.spiceproxy_conv[val]}')
# 			else:
# 				print(f'{value}')
# 		else:
# 			print(f'{value}')
# spice_config = {'ca': '-----BEGIN '
#        'CERTIFICATE-----\\nMIIFzTCCA7WgAwIBAgIUZ54fcnkh478K3ENrQPmNOtBxDA8wDQYJKoZIhvcNAQEL\\nBQAwdjEkMCIGA1UEAwwbUHJveG1veCBWaXJ0dWFsIEVudmlyb25tZW50MS0wKwYD\\nVQQLDCRiMzgwMWRlYy0zYTFjLTRhM2ItYTRkNi1kYmU0MmU1OGUwNDUxHzAdBgNV\\nBAoMFlBWRSBDbHVzdGVyIE1hbmFnZXIgQ0EwHhcNMjMwMzA1MjAwMDQ4WhcNMzMw\\nMzAyMjAwMDQ4WjB2MSQwIgYDVQQDDBtQcm94bW94IFZpcnR1YWwgRW52aXJvbm1l\\nbnQxLTArBgNVBAsMJGIzODAxZGVjLTNhMWMtNGEzYi1hNGQ2LWRiZTQyZTU4ZTA0\\nNTEfMB0GA1UECgwWUFZFIENsdXN0ZXIgTWFuYWdlciBDQTCCAiIwDQYJKoZIhvcN\\nAQEBBQADggIPADCCAgoCggIBALhzlTQ6JOhem+JgqzaSUlGio4ce/l1A9uZ1DXM4\\nbouqyvAYIpl/BK+GazT9FvbNwnW6D9oBr6jNYnzQ42nKEOGQ2wPuKEFfBs909j8T\\nStxXU7Bibj4NieatNkFx1ngOH7xSB3wYwIhkGD8LUJtp5/vgKb2wfp3s+v0MzcXQ\\nvUx2C/oj9hhO0hDbOpEjzV7zhKgoeHam7AqmNgYCc9BIY6G3MDlzjwIG2FfTIqwA\\n7brKW48LZpHgfay5mVmG5RMPsWpLbNXybfrwKvZjeD3QkzklKnrGn5aPoDd2CNUC\\nOZrIArhVKsDlaXP9t+NiuvWS1WvNJrBbPin7uwM1GJOK1q51HlisyYns6xJNB3sZ\\n9e37ZP7BIEzorm+N0wFoVp8I15hrMGxtc+zfKR/RNS7znccXdsZn1A6LxolAHwDR\\nBXKfNQ4dKe/RkSh4a6zavy+9MPfMtkBf9Kp0ZLc3dtpO0aGAeDdkJyhE1Oj6Ne3R\\ntHHATJ0RUOCEr1k5iEJPbDQnoWm2q2mIQOXaK+NBEmxyU+t2/FWjeP9qo6MISzJq\\nMLhufVZjZC01enqxoDForAxYPJ1usi2Kn1pVtrHTZNzpSqCGIT/bEl2+gIIGPfat\\nsx/l5izLe2e8zOEdiOqjoA7GRdVppzPcsmRi/5OpUfTf6tO7WKeQ5p082heyQw/W\\nV7/rAgMBAAGjUzBRMB0GA1UdDgQWBBTbviPekcqWRexRX9tUsHVQkiv2pTAfBgNV\\nHSMEGDAWgBTbviPekcqWRexRX9tUsHVQkiv2pTAPBgNVHRMBAf8EBTADAQH/MA0G\\nCSqGSIb3DQEBCwUAA4ICAQAPD38CT/1Xbh+XUFV31UbV0DG7l6lSvzEXlIXIljdX\\nJW3OzMwdzjFCEah2RumrlZJ1NmfFiVonQnMHfH47pMr3sh5mQDEcirVh30zpGyRK\\nFLAJktAofPFHgCCMz/4fqAx07Qrle5v2dehl674z98S8KGzimUfPd9dz7KawGNUi\\nF2omGqx1ELA1G0tzorZNTNibLIdo/UfvBCX3DsyztaKf0Oy7CVmfRZ8VnsKtHUtp\\nHsbNT8sz+mxzS/JTLORIdt23wdZIe9TcnXIV8f9Qwq0Cmm5E1JCejoFpWnwU5y4W\\ncH2xo/NQ5KUcUZr+hoLI9CGY1e3+RyDHVsX9vdt463Ih61LWfDgjxSEYmE3j71D0\\nolJWAKrSENyu9U/VwcYQ+z8iCzBlt08M+iIAvK+5lQaPxoHWinDYq/FbduxBMd+G\\nJF0KUZYKBA5IMb2WtzvhmaSPdhFJ22TTszIPLibbWN2F9ZGKI5dR68WwoRQRrqBZ\\n71fI1kCZ9z5d3fdEA9PVX+y9g6BKQqVPBgdIv8d10ZAJX7kHmvUfcOKYC1/+bnAP\\nZI0bGe1dpKaO6N6AhRrLeyjCwztRJHwkcVb9Fz441BMDiYZM+fvcmmje3BeapvmW\\nu+jRbs2/2HkitDS8TwqXJ7406S2FVTa4jgWID8zHUQLeun0KFfCqDB2gMhEY+SQu\\ndg==\\n-----END '
#        'CERTIFICATE-----\\n',
# HATJ0RUOCEr1k5iEJPbDQnoWm2q2mIQOXaK+NBEmxyU+t2/FWjeP9qo6MISzJq\\nMLhufVZjZC01enqxoDForAxYPJ1usi2Kn1pVtrHTZNzpSqCGIT/bEl2+gIIGPfat\\nsx/l5izLe2e8zOEdiOqjoA7GRdVppzPcsmRi/5OpUfTf6tO7WKeQ5p082heyQw/W\\nV7/rAgMBAAGjUzBRMB0GA1UdDgQWBBTbviPekcqWRexRX9tUsHVQkiv2pTAfBgNV\\nHSMEGDAWgBTbviPekcqWRexRX9tUsHVQkiv2pTAPBgNVHRMBAf8EBTADAQH/MA0G\\nCSqGSIb3DQEBCwUAA4ICAQAPD38CT/1Xbh+XUFV31UbV0DG7l6lSvzEXlIXIljdX\\nJW3OzMwdzjFCEah2RumrlZJ1NmfFiVonQnMHfH47pMr3sh5mQDEcirVh30zpGyRK\\nFLAJktAofPFHgCCMz/4fqAx07Qrle5v2dehl674z98S8KGzimUfPd9dz7KawGNUi\\nF2omGqx1ELA1G0tzorZNTNibLIdo/UfvBCX3DsyztaKf0Oy7CVmfRZ8VnsKtHUtp\\nHsbNT8sz+mxzS/JTLORIdt23wdZIe9TcnXIV8f9Qwq0Cmm5E1JCejoFpWnwU5y4W\\ncH2xo/NQ5KUcUZr+hoLI9CGY1e3+RyDHVsX9vdt463Ih61LWfDgjxSEYmE3j71D0\\nolJWAKrSENyu9U/VwcYQ+z8iCzBlt08M+iIAvK+5lQaPxoHWinDYq/FbduxBMd+G\\nJF0KUZYKBA5IMb2WtzvhmaSPdhFJ22TTszIPLibbWN2F9ZGKI5dR68WwoRQRrqBZ\\n71fI1kCZ9z5d3fdEA9PVX+y9g6BKQqVPBgdIv8d10ZAJX7kHmvUfcOKYC1/+bnAP\\nZI0bGe1dpKaO6N6AhRrLeyjCwztRJHwkcVb9Fz441BMDiYZM+fvcmmje3BeapvmW\\nu+jRbs2/2HkitDS8TwqXJ7406S2FVTa4jgWID8zHUQLeun0KFfCqDB2gMhEY+SQu\\ndg==\\n-----END '
#        'CERTIFICATE-----\\n',
# i2Kn1pVtrHTZNzpSqCGIT/bEl2+gIIGPfat\\nsx/l5izLe2e8zOEdiOqjoA7GRdVppzPcsmRi/5OpUfTf6tO7WKeQ5p082heyQw/W\\nV7/rAgMBAAGjUzBRMB0GA1UdDgQWBBTbviPekcqWRexRX9tUsHVQkiv2pTAfBgNV\\nHSMEGDAWgBTbviPekcqWRexRX9tUsHVQkiv2pTAPBgNVHRMBAf8EBTADAQH/MA0G\\nCSqGSIb3DQEBCwUAA4ICAQAPD38CT/1Xbh+XUFV31UbV0DG7l6lSvzEXlIXIljdX\\nJW3OzMwdzjFCEah2RumrlZJ1NmfFiVonQnMHfH47pMr3sh5mQDEcirVh30zpGyRK\\nFLAJktAofPFHgCCMz/4fqAx07Qrle5v2dehl674z98S8KGzimUfPd9dz7KawGNUi\\nF2omGqx1ELA1G0tzorZNTNibLIdo/UfvBCX3DsyztaKf0Oy7CVmfRZ8VnsKtHUtp\\nHsbNT8sz+mxzS/JTLORIdt23wdZIe9TcnXIV8f9Qwq0Cmm5E1JCejoFpWnwU5y4W\\ncH2xo/NQ5KUcUZr+hoLI9CGY1e3+RyDHVsX9vdt463Ih61LWfDgjxSEYmE3j71D0\\nolJWAKrSENyu9U/VwcYQ+z8iCzBlt08M+iIAvK+5lQaPxoHWinDYq/FbduxBMd+G\\nJF0KUZYKBA5IMb2WtzvhmaSPdhFJ22TTszIPLibbWN2F9ZGKI5dR68WwoRQRrqBZ\\n71fI1kCZ9z5d3fdEA9PVX+y9g6BKQqVPBgdIv8d10ZAJX7kHmvUfcOKYC1/+bnAP\\nZI0bGe1dpKaO6N6AhRrLeyjCwztRJHwkcVb9Fz441BMDiYZM+fvcmmje3BeapvmW\\nu+jRbs2/2HkitDS8TwqXJ7406S2FVTa4jgWID8zHUQLeun0KFfCqDB2gMhEY+SQu\\ndg==\\n-----END '
#        'CERTIFICATE-----\\n',
# 2heyQw/W\\nV7/rAgMBAAGjUzBRMB0GA1UdDgQWBBTbviPekcqWRexRX9tUsHVQkiv2pTAfBgNV\\nHSMEGDAWgBTbviPekcqWRexRX9tUsHVQkiv2pTAPBgNVHRMBAf8EBTADAQH/MA0G\\nCSqGSIb3DQEBCwUAA4ICAQAPD38CT/1Xbh+XUFV31UbV0DG7l6lSvzEXlIXIljdX\\nJW3OzMwdzjFCEah2RumrlZJ1NmfFiVonQnMHfH47pMr3sh5mQDEcirVh30zpGyRK\\nFLAJktAofPFHgCCMz/4fqAx07Qrle5v2dehl674z98S8KGzimUfPd9dz7KawGNUi\\nF2omGqx1ELA1G0tzorZNTNibLIdo/UfvBCX3DsyztaKf0Oy7CVmfRZ8VnsKtHUtp\\nHsbNT8sz+mxzS/JTLORIdt23wdZIe9TcnXIV8f9Qwq0Cmm5E1JCejoFpWnwU5y4W\\ncH2xo/NQ5KUcUZr+hoLI9CGY1e3+RyDHVsX9vdt463Ih61LWfDgjxSEYmE3j71D0\\nolJWAKrSENyu9U/VwcYQ+z8iCzBlt08M+iIAvK+5lQaPxoHWinDYq/FbduxBMd+G\\nJF0KUZYKBA5IMb2WtzvhmaSPdhFJ22TTszIPLibbWN2F9ZGKI5dR68WwoRQRrqBZ\\n71fI1kCZ9z5d3fdEA9PVX+y9g6BKQqVPBgdIv8d10ZAJX7kHmvUfcOKYC1/+bnAP\\nZI0bGe1dpKaO6N6AhRrLeyjCwztRJHwkcVb9Fz441BMDiYZM+fvcmmje3BeapvmW\\nu+jRbs2/2HkitDS8TwqXJ7406S2FVTa4jgWID8zHUQLeun0KFfCqDB2gMhEY+SQu\\ndg==\\n-----END '
#        'CERTIFICATE-----\\n',
# V0DG7l6lSvzEXlIXIljdX\\nJW3OzMwdzjFCEah2RumrlZJ1NmfFiVonQnMHfH47pMr3sh5mQDEcirVh30zpGyRK\\nFLAJktAofPFHgCCMz/4fqAx07Qrle5v2dehl674z98S8KGzimUfPd9dz7KawGNUi\\nF2omGqx1ELA1G0tzorZNTNibLIdo/UfvBCX3DsyztaKf0Oy7CVmfRZ8VnsKtHUtp\\nHsbNT8sz+mxzS/JTLORIdt23wdZIe9TcnXIV8f9Qwq0Cmm5E1JCejoFpWnwU5y4W\\ncH2xo/NQ5KUcUZr+hoLI9CGY1e3+RyDHVsX9vdt463Ih61LWfDgjxSEYmE3j71D0\\nolJWAKrSENyu9U/VwcYQ+z8iCzBlt08M+iIAvK+5lQaPxoHWinDYq/FbduxBMd+G\\nJF0KUZYKBA5IMb2WtzvhmaSPdhFJ22TTszIPLibbWN2F9ZGKI5dR68WwoRQRrqBZ\\n71fI1kCZ9z5d3fdEA9PVX+y9g6BKQqVPBgdIv8d10ZAJX7kHmvUfcOKYC1/+bnAP\\nZI0bGe1dpKaO6N6AhRrLeyjCwztRJHwkcVb9Fz441BMDiYZM+fvcmmje3BeapvmW\\nu+jRbs2/2HkitDS8TwqXJ7406S2FVTa4jgWID8zHUQLeun0KFfCqDB2gMhEY+SQu\\ndg==\\n-----END '
#        'CERTIFICATE-----\\n',
# fvBCX3DsyztaKf0Oy7CVmfRZ8VnsKtHUtp\\nHsbNT8sz+mxzS/JTLORIdt23wdZIe9TcnXIV8f9Qwq0Cmm5E1JCejoFpWnwU5y4W\\ncH2xo/NQ5KUcUZr+hoLI9CGY1e3+RyDHVsX9vdt463Ih61LWfDgjxSEYmE3j71D0\\nolJWAKrSENyu9U/VwcYQ+z8iCzBlt08M+iIAvK+5lQaPxoHWinDYq/FbduxBMd+G\\nJF0KUZYKBA5IMb2WtzvhmaSPdhFJ22TTszIPLibbWN2F9ZGKI5dR68WwoRQRrqBZ\\n71fI1kCZ9z5d3fdEA9PVX+y9g6BKQqVPBgdIv8d10ZAJX7kHmvUfcOKYC1/+bnAP\\nZI0bGe1dpKaO6N6AhRrLeyjCwztRJHwkcVb9Fz441BMDiYZM+fvcmmje3BeapvmW\\nu+jRbs2/2HkitDS8TwqXJ7406S2FVTa4jgWID8zHUQLeun0KFfCqDB2gMhEY+SQu\\ndg==\\n-----END '
#        'CERTIFICATE-----\\n',
# cYQ+z8iCzBlt08M+iIAvK+5lQaPxoHWinDYq/FbduxBMd+G\\nJF0KUZYKBA5IMb2WtzvhmaSPdhFJ22TTszIPLibbWN2F9ZGKI5dR68WwoRQRrqBZ\\n71fI1kCZ9z5d3fdEA9PVX+y9g6BKQqVPBgdIv8d10ZAJX7kHmvUfcOKYC1/+bnAP\\nZI0bGe1dpKaO6N6AhRrLeyjCwztRJHwkcVb9Fz441BMDiYZM+fvcmmje3BeapvmW\\nu+jRbs2/2HkitDS8TwqXJ7406S2FVTa4jgWID8zHUQLeun0KFfCqDB2gMhEY+SQu\\ndg==\\n-----END '
#        'CERTIFICATE-----\\n',
# 9ZGKI5dR68WwoRQRrqBZ\\n71fI1kCZ9z5d3fdEA9PVX+y9g6BKQqVPBgdIv8d10ZAJX7kHmvUfcOKYC1/+bnAP\\nZI0bGe1dpKaO6N6AhRrLeyjCwztRJHwkcVb9Fz441BMDiYZM+fvcmmje3BeapvmW\\nu+jRbs2/2HkitDS8TwqXJ7406S2FVTa4jgWID8zHUQLeun0KFfCqDB2gMhEY+SQu\\ndg==\\n-----END '
#        'CERTIFICATE-----\\n',
# 4jgWID8zHUQLeun0KFfCqDB2gMhEY+SQu\\ndg==\\n-----END '
#        'CERTIFICATE-----\\n',
#  'delete-this-file': 1,
#  'delete-this-file': 1,
#  'host': 'pvespiceproxy:67cd6655:301:pve1::c6b5de0447e253a0b0994727eebcda3b5173402e',
#  'host': 'pvespiceproxy:67cd6655:301:pve1::c6b5de0447e253a0b0994727eebcda3b5173402e',
#  'host-subject': 'OU=PVE Cluster Node,O=Proxmox Virtual '
#                  'Environment,CN=pve1.kaowei.tw',
#  'password': 'a01e52b7f1ef5c8023ae75640a1c3e39c7e00177',
#  'proxy': 'http://pve1.kaowei.tw:3128',
#  'release-cursor': 'Ctrl+Alt+R',
#  'secure-attention': 'Ctrl+Alt+Ins',
#  'title': 'VM 301 - Win10-01',
#  'tls-port': 61001,
#  'toggle-fullscreen': 'Shift+F11',
#  'type': 'spice'}