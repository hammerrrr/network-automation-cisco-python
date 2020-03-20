from netmiko import ConnectHandler
import yaml
import time
import os
import datetime

"""
    @author: Ilham Syah
    @YearOf: 2018
    @Purpose: ~
"""

def banner():
    text = r"""
             _   _      _                 _        
            | \ | |    | |     /\        | |       
            |  \| | ___| |_   /  \  _   _| |_ ___  
            | . ` |/ _ \ __| / /\ \| | | | __/ _ \ 
            | |\  |  __/ |_ / ____ \ |_| | || (_) |
            |_| \_|\___|\__/_/    \_\__,_|\__\___/                                                       
                                         
           """
    print("="*62)
    print(text)
    print("""           
            Network Automation Script with Python
                        @_ham.sh | 2018
                    facebook.com/nilham.92
                          Alpha Test
         """)
    print("="*62)
    print("="*62)
    print("")


"""
OPEN YAML DATA CONFIGURATION
"""
with open("playbooks/data-rip.yml") as f:
    data = yaml.load(f)
data_config = data['CORE']['config']


class Netautomation():


    """
    __INIT__ 
    """
    def __init__(self, items):
        self.input(items)

    """
    GET USER INPUT METHOD 
    """
    def input(self, items):
        banner()
        text = "Fitur Network Automasi: \n(1) Cek Konfigurasi\n(2) Konfigurasi Interface\n(3) Konfigurasi RIPv2\n(4) Backup Configuration"
        print(text)
        print("")
        self.fiturinput = int(input("Pilih Fitur: "))
        self.getCredentials(items)

        
        

    """
    GET CREDENTIALS METHOD 
    """  
    def getCredentials(self, items):
        # Get Device Credentials
        for item in items:

            # Get Device Host, Name, Type, Username, and Password
            host            = item['host']
            self.name       = item['name']
            username        = item['username']
            password        = item['password']
            device_type     = item['device_type']

            # Device Credentials for Netmiko
            device_credentials = {
                'device_type': device_type,
                'ip': host,
                'username': username,
                'password': password
            }

            # print(device_credentials) # print device credentials
            # Connect Device to Netmiko ConnectHandler
            self.connect = ConnectHandler(**device_credentials)

            text = "||  Device Credentials  ||"
            print("")
            print("="*len(text) + "\n" + text + "\n" +"="*len(text))
            print("Device Name  :", self.name)
            print("Device Host  :", host)
            print("Username     :", username)
            print("Password     :", password)
            print("Device Type  :", device_type)
            print("")
            time.sleep(.5)

            
            if self.fiturinput == 1:
                self.check_configuration()
            elif self.fiturinput == 2:
                self.configure_interface(item)
            elif self.fiturinput == 3:
                self.configure_rip(item)
            elif self.fiturinput == 4:
                self.backup_config(item)
            else:
                print("invalid input")
                self.fiturinput = int(input("Pilih Fitur: "))
            
    

    """
    CHECK CONFIGURATION METHOD
    """
    def check_configuration(self):

        # Interface Configuration
        text = ("| Device {} Configuration |").format(self.name)
        print("")
        print("-"*len(text) + "\n" + text + "\n" +"-"*len(text))
        interface_conf = self.connect.send_command("sh run")
        print(interface_conf)

       
    """
    INTERFACE CONFIGURATION METHOD
    """
    def configure_interface(self, item):

        text = "Configuring Interface"
        print("-" *len(text) + "\n" + text + " \n" + "-"*len(text))

        for config_interface in item['config_interface']:
            interface   = config_interface['interface']
            address     = config_interface['ip_address']
            netmask     = config_interface['netmask']

            confInterface   = "int " + interface
            ip_address      = ("ip add {} {}").format(address, netmask)

            if 'no_shut' in config_interface and config_interface['no_shut'] == True:
                no_shut = "no shutdown"
            
            config = []
            config.append(confInterface)
            config.append(ip_address)
            config.append(no_shut)
            # print(config) # debug OK

            print("Interface        :", interface)
            print("-- IP Address    :", address)
            print("-- Netmask       :", netmask)
           
            print("")
            print("Succesfully Configuring Interface", interface)
            print("")

            time.sleep(.5)

            # Send Command Config list into Device via Netmiko ConnectHandler
            self.connect.send_config_set(config)

            
            self.save_config(item)


    """
    RIP CONFIGURATION METHOD
    """
    def configure_rip(self, item):

        for rip in item['config_rip']:
            #print(rip) # debug OK
            rip_conf     = "router rip"
            rip_ver      = str(rip['version'])
            rip_network  = rip['network']
            rip_ver_conf = "version " + rip_ver

            config = []
            config.append(rip_conf)
            config.append(rip_ver_conf)
            
            for net in rip_network:
                rip_net = "network " + net
                config.append(rip_net)
            
            text = "Configuring RIPv " + rip_ver_conf

            print("-"*len(text) + "\n" + text + "\n" + "-"*len(text))
            print("-- Routing Protocol  : RIP")
            print("-- Version           :", rip_ver)
            print("-- Network           :", rip_network)
            print("")
            time.sleep(.5)

            # Send Command Config list into Device via Netmiko ConnectHandler
            self.connect.send_config_set(config)

            
            self.save_config(item)
    
    """
    SAVE CONFIGURATION METHOD 
    """
    def save_config(self, item):
       
        for configuration in item['configuration']:

            if 'save' in configuration and configuration['save'] == True:
                text = "Saving Configuration "
                print("-" *len(text) + "\n" + text + " \n" + "-"*len(text))
                print("")
                time.sleep(.5)

                # Send command to devices to write configuration on NVRAM/disk
                print(self.connect.send_command("wr"))

    """
    BACKUP CONFIGURATION METHOD 
    """
    def backup_config(self, item):
       
        for configuration in item['configuration']:
            
            if 'backup' in configuration and configuration['backup'] == True:
            
                folder_path = "Backup"
                date        = datetime.datetime.now()
                file_date   = date.date()
                file_name   = ("{}/backup_{}_{}.txt").format(folder_path,self.name,file_date)
                file_conf = self.connect.send_command("sh run")
                
                text = " Saving Configuration as " + file_name
                print("-" *len(text) + "\n" + text + " \n" + "-"*len(text))

                if(not os.path.isdir(folder_path)):
                    os.system("mkdir {0} && chmod 755 {0}".format(folder_path))

                with open(file_name, 'w') as f:
                    f.write(file_conf)
                    
                

netauto = Netautomation(data_config)
