import telnetlib
from telnetlib import Telnet
import json
import socket

task = "ftp-check"
timeout_sec = 5

with open('input_check_list.json') as file:
  data = json.load(file)
print(data)

def get_Host_name_IP():
    try:
        host_name = socket.gethostname()
        host_ip = socket.gethostbyname(host_name)
        print("Hostname :  ",host_name)
        print("IP : ",host_ip)
        return host_ip, host_name
    except:
        print("Unable to get Hostname and IP")

def check_conn(data, host_ip, host_name):
    o_json_dict = {}
    for domain, ports in data.items():
        o_ports_list = []
        for port in ports:
            print(domain, port)
            try:
                tlnt = telnetlib.Telnet(domain,port,timeout_sec)
                tlnt.close()
                print("Connection Pass: Domain = %s, Port = %i \n" % (domain, port))
                status = [port, "Passed", "NA"]
                o_ports_list.append(status)
            except Exception as err:
                print("Failed: Domain = %s, Port = %i \n" % (domain, port))
                print("Error: %s \n" % (err))
                errorstatus = "Error = " + str(err)
                status = [port, "Failed", errorstatus]
                o_ports_list.append(status)
        o_json_dict[domain] = o_ports_list

    print(o_json_dict)
    outputfile = host_ip + "_" + host_name + "_" + task + ".json"
    with open(outputfile, 'w') as file1:
        file1.write(json.dumps(o_json_dict))

host_ip, host_name = get_Host_name_IP()

print(host_ip, host_name)
check_conn(data, host_ip, host_name)