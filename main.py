from librouteros import connect
import librouteros
import pprint
import json
import time
import re
import getpass

host = input("🚧 Host: ")
username = input("🚧 Username: ")
password = getpass.getpass("   Password: ")

conf = {
	"host": host,
	"username":username,
	"password":password
}


def create_json(data, filename):
	with open(filename, 'w') as file:
		json.dump(data, file,indent=4)


def exec_command(cmd): # Launch a command
	value = []
	data = conn(cmd)
	if isinstance(data, str): # Valid String in Output
	    lines = data.strip().split("\n")
	    for line in lines:
	        if line.startswith("#"):
	            continue
	        if line.startswith("/"):
	            value.append({})
	            continue
	        key, val = line.split("=", 1)
	        value[-1][key] = val
	else:
	    for a in data:
	        value.append(a)
	return value

def speed_test(host,username,password,address):
		# Configuración del router MikroTik
		host = host
		username = username
		password = password

		# Conexión al router MikroTik
		api = connect(host=host, username=username, password=password)

		# Ejecución del speed-test
		result = api(cmd='/tool/speed-test', address=address, user=username, password=password, duration="30")
		speed = []
		data = {
			"speed": speed,
			"wan": address
		}
		for a in result:
		    speed.append(a)
		return speed

#--------------------------------------------------------------#
# OUTPUT generate by function analyze_json()                   #
# If you want modify output, please check the function analyze #
#--------------------------------------------------------------#

def analyze_json_atp(data): # Generate Analyze ATP
	pprint.pprint(data)
	# Hostname
	print('\n------------------- 𝓗𝓸𝓼𝓽𝓷𝓪𝓶𝓮 ----------------------- \n')
	print(f"🏠  {data['hostnames'][0]['name']}\n")
	

	# IP address
	print('\n------------------- 𝓘𝓟 𝓐𝓭𝓭𝓻𝓮𝓼𝓼 --------------------- \n')
	ip = []
	ips_links = '^100\.113\.[0-9]{1,3}\.[0-9]{1,3}$'
	ips_wan = '^100\.125\.[0-9]{1,3}\.[0-9]{1,3}$'
	ips_lo = '^100\.127\.[0-9]{1,3}\.[0-9]{1,3}$'
	ips_customer = '^100\.[0-9]{1,3}\.[0-9]{1,3}\.1$'
	for a in data['ipaddress']:
		ips = a['address'].split('/')
		ips = ips[0]
		if re.match(ips_links,ips):
			print(f'✅ IPs Radio: {ips}')
		elif re.match(ips_customer,ips):
			print(f'✅ IPs Customer: {ips}')
		elif re.match(ips_wan,ips):
			print(f'✅ IPs WAN: {ips}')
		elif re.match(ips_lo, ips):
			print(f'✅ IPs Lo0: {ips}')
    

    # Interfaces
	print('\n------------------ 𝓘𝓷𝓽𝓮𝓻𝓯𝓪𝓬𝓮𝓼 ---------------------- \n')
	inter = data['interface']
	for a in inter:
		if a['speed'] == '1Gbps' or a['speed'] == '10Gbps':
			print(f"✅ Interface {a['name']} mtu {a['mtu']} {a['speed']} ")
		else:
			print(f"❌ Interface {a['name']} {a['speed']}")


	# Neighbors
	print('\n------------------- 𝓝𝓮𝓲𝓰𝓱𝓫𝓸𝓻 ----------------------- \n')
	neighbors = []
	for a in data['neighbors']:
		identity = a['identity']
		identity = identity.split('_')
		fin_identity = "_".join(identity)

		if 'CN' in identity:
			print(f'✅ Neighbor: {fin_identity}')
		else:
			print(f'⚠️ Others: {fin_identity}')


	# OSPF Neighbor
	print('\n----------------------- 𝓞𝓢𝓟𝓕 ----------------------- \n')
	wan = ''
	count = 0
	for a in data['ospf-neighbor']:
		count += 1
		wan = a['address']
		print(f"✅ Neighbor: {a['address']} - {a['state']} - {a['adjacency']} - {a['interface']}")


	# OSPF LSAs
	print('\n----------------------- 𝓞𝓢𝓟𝓕 ----------------------- \n')
	default = []
	for a in data['ospf']:
		if a['id'] == '0.0.0.0':
			default.append({'id':a['id'],'type':a['type'],'originator':a['originator']})
	if len(default) == 2:
		print(f'✅ Default: {default[0]["id"]} - Originator: {default[0]["originator"]}')
		print(f'✅ Default: {default[1]["id"]} - Originator: {default[1]["originator"]}')
	elif len(default) > 2 :
		print('⚠️ LSAs (> 2) ')
		print(f'❌ Default: {default[0]["id"]} - Originator: {default[0]["originator"]}')
		print(f'❌ Default: {default[1]["id"]} - Originator: {default[1]["originator"]}')
		print(f'❌ Default: {default[2]["id"]} - Originator: {default[2]["originator"]}')
	elif len(default)  == 1:
		print(f'❌ Default: {default[0]["id"]} - Originator: {default[0]["originator"]}')
	else:
		print('❌ Not Found LSAs')


	# Radius
	print('\n--------------------- Radius ----------------------- \n')
	if len(data['radius']) > 0:	
		for a in data['radius']:
			print('✅')
			print(f"comment: {a['comment']} ")
			print(f"address: {a['address']}")
			print(f"service: {a['service']} ")
			print(f"proto: {a['protocol']}")
	else:
		print('❌ Not exist radius')


	#Speed-test
	print('\n------------------- Speed-test WAN ------------------\n')
	speed = data['speed-test'][-1]


	tcpdownload = data['speed-test'][-1]['tcp-download'].split(' ')[0]
	tcpupload = data['speed-test'][-1]['tcp-upload'].split(' ')[0]

	regex_Gbps = r"[0-9]+\.*[0-9]*Gbps"
	regex_Mbps = r"[0-9]+\.*[0-9]*Mbps"
	regex_bps = r"[0-9]+\.*[0-9]*bps"

	if re.match(regex_Mbps, tcpdownload):
		download = tcpdownload.split('Mbps')[0]
		upload = tcpupload.split('Mbps')[0]

		
		if int(download) < 500:	# If Download < 500M 
			print(f"✅ Address: {wan}")
			print(f"❌ TCP Download: {tcpdownload}")
			print(f"✅ TCP Upload: {tcpupload}")
			print(f"✅ Jitter {speed['jitter-min-avg-max']}")
			print(f"✅ Ping: {speed['ping-min-avg-max']}")

		elif int(upload) < 500: # If Upload < 500M
			print(f"✅ Address: {wan}")
			print(f"✅ TCP Download: {tcpdownload}")
			print(f"❌ TCP Upload: {tcpupload}")
			print(f"✅ Jitter {speed['jitter-min-avg-max']}")
			print(f"✅ Ping: {speed['ping-min-avg-max']}")

		else: 					# Else everything ok ...
			print(f"✅ Address: {wan}")
			print(f"✅ TCP Download: {tcpdownload}")
			print(f"✅ TCP Upload: {tcpupload}")
			print(f"✅ Jitter {speed['jitter-min-avg-max']}")
			print(f"✅ Ping: {speed['ping-min-avg-max']}")
	elif re.match(regex_Mbps, tcpupload):
		download = tcpdownload.split('Mbps')[0]
		upload = tcpupload.split('Mbps')[0]

		if int(download) < 500:	# If Download < 500M 
			print(f"✅ Address: {wan}")
			print(f"❌ TCP Download: {tcpdownload}")
			print(f"✅ TCP Upload: {tcpupload}")
			print(f"✅ Jitter {speed['jitter-min-avg-max']}")
			print(f"✅ Ping: {speed['ping-min-avg-max']}")

		elif int(upload) < 500: # If Upload < 500M
			print(f"✅ Address: {wan}")
			print(f"✅ TCP Download: {tcpdownload}")
			print(f"❌ TCP Upload: {tcpupload}")
			print(f"✅ Jitter {speed['jitter-min-avg-max']}")
			print(f"✅ Ping: {speed['ping-min-avg-max']}")
			
		else: 					# Else everything ok ...
			print(f"✅ Address: {wan}")
			print(f"✅ TCP Download: {tcpdownload}")
			print(f"✅ TCP Upload: {tcpupload}")
			print(f"✅ Jitter {speed['jitter-min-avg-max']}")
			print(f"✅ Ping: {speed['ping-min-avg-max']}")
	elif re.match(regex_bps, tcpdownload):
		download = tcpdownload.split('Mbps')[0]
		upload = tcpupload.split('Mbps')[0]

		print(f"✅ Address: {wan}")
		print(f"❌ TCP Download: {tcpdownload}")
		print(f"❌ TCP Upload: {tcpupload}")
		print(f"✅ Jitter {speed['jitter-min-avg-max']}")
		print(f"✅ Ping: {speed['ping-min-avg-max']}")
	
	elif re.match(regex_bps, tcpupload):
		download = tcpdownload.split('Mbps')[0]
		upload = tcpupload.split('Mbps')[0]

		print(f"✅ Address: {wan}")
		print(f"❌ TCP Download: {tcpdownload}")
		print(f"❌ TCP Upload: {tcpupload}")
		print(f"✅ Jitter {speed['jitter-min-avg-max']}")
		print(f"✅ Ping: {speed['ping-min-avg-max']}")

	elif re.match(regex_Gbps, tcpdownload):
		print(f"✅ Address: {wan}")
		print(f"✅ TCP Download: {tcpdownload}")
		print(f"✅ TCP Upload: {tcpupload}")
		print(f"✅ Jitter {speed['jitter-min-avg-max']}")
		print(f"✅ Ping: {speed['ping-min-avg-max']}")
	
	elif re.match(regex_Gbps, tcpupload):
		print(f"✅ Address: {wan}")
		print(f"✅ TCP Download: {tcpdownload}")
		print(f"✅ TCP Upload: {tcpupload}")
		print(f"✅ Jitter {speed['jitter-min-avg-max']}")
		print(f"✅ Ping: {speed['ping-min-avg-max']}")



	# Speed-test CORE
	print('\n----------------- Speed-test CORE -----------------\n')
	speed = data['speed-test-core'][-1]


	tcpdownload = data['speed-test-core'][-1]['tcp-download'].split(' ')[0]
	tcpupload = data['speed-test-core'][-1]['tcp-upload'].split(' ')[0]

	regex_Gbps = r"[0-9]+\.*[0-9]*Gbps"
	regex_Mbps = r"[0-9]+\.*[0-9]*Mbps"
	regex_bps = r"[0-9]+\.*[0-9]*bps"

	if re.match(regex_Mbps, tcpdownload):
		download = tcpdownload.split('Mbps')[0]
		upload = tcpupload.split('Mbps')[0]

		
		if int(download) < 500:	# If Download < 500M 
			print(f"✅ Address: 100.127.0.3")
			print(f"❌ TCP Download: {tcpdownload}")
			print(f"✅ TCP Upload: {tcpupload}")
			print(f"✅ Jitter {speed['jitter-min-avg-max']}")
			print(f"✅ Ping: {speed['ping-min-avg-max']}")

		elif int(upload) < 500: # If Upload < 500M
			print(f"✅ Address: 100.127.0.3")
			print(f"✅ TCP Download: {tcpdownload}")
			print(f"❌ TCP Upload: {tcpupload}")
			print(f"✅ Jitter {speed['jitter-min-avg-max']}")
			print(f"✅ Ping: {speed['ping-min-avg-max']}")

		else: 					# Else everything ok ...
			print(f"✅ Address: 100.127.0.3")
			print(f"✅ TCP Download: {tcpdownload}")
			print(f"✅ TCP Upload: {tcpupload}")
			print(f"✅ Jitter {speed['jitter-min-avg-max']}")
			print(f"✅ Ping: {speed['ping-min-avg-max']}")
	elif re.match(regex_Mbps, tcpupload):
		download = tcpdownload.split('Mbps')[0]
		upload = tcpupload.split('Mbps')[0]

		if int(download) < 500:	# If Download < 500M 
			print(f"✅ Address: 100.127.0.3")
			print(f"❌ TCP Download: {tcpdownload}")
			print(f"✅ TCP Upload: {tcpupload}")
			print(f"✅ Jitter {speed['jitter-min-avg-max']}")
			print(f"✅ Ping: {speed['ping-min-avg-max']}")

		elif int(upload) < 500: # If Upload < 500M
			print(f"✅ Address: 100.127.0.3")
			print(f"✅ TCP Download: {tcpdownload}")
			print(f"❌ TCP Upload: {tcpupload}")
			print(f"✅ Jitter {speed['jitter-min-avg-max']}")
			print(f"✅ Ping: {speed['ping-min-avg-max']}")
			
		else: 					# Else everything ok ...
			print(f"✅ Address: 100.127.0.3")
			print(f"✅ TCP Download: {tcpdownload}")
			print(f"✅ TCP Upload: {tcpupload}")
			print(f"✅ Jitter {speed['jitter-min-avg-max']}")
			print(f"✅ Ping: {speed['ping-min-avg-max']}")
	elif re.match(regex_bps, tcpdownload):
		download = tcpdownload.split('Mbps')[0]
		upload = tcpupload.split('Mbps')[0]

		print(f"✅ Address: 100.127.0.3")
		print(f"❌ TCP Download: {tcpdownload}")
		print(f"❌ TCP Upload: {tcpupload}")
		print(f"✅ Jitter {speed['jitter-min-avg-max']}")
		print(f"✅ Ping: {speed['ping-min-avg-max']}")
	
	elif re.match(regex_bps, tcpupload):
		download = tcpdownload.split('Mbps')[0]
		upload = tcpupload.split('Mbps')[0]

		print(f"✅ Address: 100.127.0.3")
		print(f"❌ TCP Download: {tcpdownload}")
		print(f"❌ TCP Upload: {tcpupload}")
		print(f"✅ Jitter {speed['jitter-min-avg-max']}")
		print(f"✅ Ping: {speed['ping-min-avg-max']}")

	elif re.match(regex_Gbps, tcpdownload):
		print(f"✅ Address: 100.127.0.3")
		print(f"✅ TCP Download: {tcpdownload}")
		print(f"✅ TCP Upload: {tcpupload}")
		print(f"✅ Jitter {speed['jitter-min-avg-max']}")
		print(f"✅ Ping: {speed['ping-min-avg-max']}")
	
	elif re.match(regex_Gbps, tcpupload):
		print(f"✅ Address: 100.127.0.3")
		print(f"✅ TCP Download: {tcpdownload}")
		print(f"✅ TCP Upload: {tcpupload}")
		print(f"✅ Jitter {speed['jitter-min-avg-max']}")
		print(f"✅ Ping: {speed['ping-min-avg-max']}")



	print('\n----- Script Generated by Eirikr -----\n')

	

try:
	conn = librouteros.connect(
	host=conf['host'],
	username=conf['username'],
	password=conf['password']
	)

	print('☕ Please wait a moment... \n')
	# Launch Commands
	hostnames = exec_command(cmd='/system/identity/print')
	interface = exec_command(cmd='/interface/ethernet/print')
	ipaddress = exec_command(cmd='/ip/address/print')
	neighbors = exec_command(cmd='/ip/neighbor/print')
	radius  = exec_command(cmd='/radius/print')
	ospf_lsa  = exec_command(cmd='/routing/ospf/lsa/print')
	ospf_neighbor = exec_command(cmd='/routing/ospf/neighbor/print')
	speed_test_wan = speed_test(conf['host'],conf['username'],conf['password'],ospf_neighbor[0]['address'])
	speed_test_core = speed_test(conf['host'],conf['username'],conf['password'],'100.127.0.3')

	# Filters 
	hostname  = [{'name':el['name']} for el in hostnames]
	interface = [{'name':el['name'],'speed':el['speed'],'mtu':el['mtu']} for el in interface]
	ipaddress = [{'interface':el['interface'],'address':el['address']} for el in ipaddress]
	neighbors = [{'interface':el['interface'],'identity':el['identity'],'mac-address':el['mac-address']} for el in neighbors]
	radius = [{'comment':el['comment'],'address':el['address'],'src-address':el['src-address'],'protocol':el['protocol'],'service':el['service']} for el in radius]
	ospf_lsa = [{'area':el['area'],'id':el['id'],'type':el['type'], 'originator':el['originator']} for el in ospf_lsa]
	ospf_neighbor = [{'address':el['address'],'state':el['state'],'adjacency':el['adjacency'], 'interface':el['interface']} for el in ospf_neighbor]

	# Generate Object with Filters
	data = {}

	data['hostnames'] = hostnames 
	data['interface'] = interface
	data['ipaddress'] = ipaddress
	data['neighbors'] = neighbors
	data['radius'] = radius
	data['ospf-neighbor'] = ospf_neighbor
	data['ospf'] = ospf_lsa
	data['speed-test'] = speed_test_wan
	data['speed-test-core'] = speed_test_core

	# Generate ATP Analyze
	analyze_json_atp(data)

except ConnectionRefusedError:
	print('Please allow API Port ☕')
except KeyboardInterrupt:
	print('Bye ...')
