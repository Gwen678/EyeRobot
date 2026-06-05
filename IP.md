In the ERC pole, but more generally in many situation, you will need a static IP, or setup Wifi on a RPI with Ubuntu (server or not).

## Ubuntu Server on RPI

To add a new wifi connection in an ubuntu server of a RPI, you can

- go inside the configuration folder: /etc/netplan
- Inside this path there is a yaml file that you can open and add new networks. To open it, use `sudo nano <file.yaml>`
- To add a wifi connection, the RPI has a wifi module with the interface called wlan0. Modifiy the yaml file in this way (see the wifi part).
    
    ```python
    network:
        ethernets:
            eth0:
                dhcp4: true
                optional: true
        version: 2
        wifis:
            wlan0:
                optional: true
                access-points:
                    "SSID-NAME-HERE":
                        password: "PASSWORD"
                dhcp4: true
    ```
    

- To apply the changes, run

```python
sudo netplan apply
sudo reboot
```

In many cases, you need to add a static IP address. You can modify the same file if you’re on Ubuntu Server. Assuming that you want to add a static IP address for some ethernet interface, you can modifiy the same file as shown below. 

```python
network:
  ethernets:
    eth0:
      addresses:
        - 192.168.1.247/24
  version: 2
```

Note that if you want your raspberry to be connected to the Internet with this IP (assuming your modem is connected to the Internet, which is not our case), you need to specify DNS servers and the gateway. For more information → https://www.linuxtechi.com/static-ip-address-on-ubuntu-server/

Additionally, don’t forget to remove the line dhcp4 for some network interface if you don’t want the DHCP server assigns you another IP. With the example of before with the static IP, no dhcp4 is mentionned. To apply the changes, run 

```python
sudo netplan apply
sudo reboot # recommended
```

## Static IPs (Ubuntu Desktop) using GUI

To add a static IP address is also simple. Using your computer for example with the GUI

- Connect your device to the network that you want to use to communicate with another device
- Go to Network Settings
- On the network, click on the gear icon for wired connection
- On the IPv4 tab, follow the next screenshot (leave the DNS empty) with YOUR choice of IP
    - For our network, the mask is also 255.255.255.0 and the gateway is 169.254.55.1. The choice of this IP should follow the rules of
    
    Network Architecture
    
    - Ask your TL to assign a correct IP.
    

!image.png

### Using nmcli

If you need to install it: https://computingforgeeks.com/install-and-use-networkmanager-nmcli-on-ubuntu-debian/ 

```python
nmcli connection show
```

This command above will show you all network interfaces. To set a static IP, choose your interface and run the 3 commands, replacing the IP and the mask

```python
sudo nmcli c mod "the name of the interface" ipv4.address <ip>/<mask> ipv4.method manual
sudo nmcli c up "the name of the interface"
sudo reboot
```

Note that using this tool, the yaml file may be not updated but it’s ok, you can get the final configuration using 

```python
nmcli netplan get
```
