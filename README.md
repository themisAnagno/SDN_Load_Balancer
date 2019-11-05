# SDN Load Balancer on OpenStack SDN/NFV platform

## Prerequisites
* pip3

## Installation
Clone the repository
```
git clone https://github.com/themisAnagno/SDN_Load_Balancer.git
cd SDN_Load_Balancer
```
Create the Virtual Environment.
```
pip3 install virtualenv
virtualenv venv --python=python3.7
source venv/bin/activate
```

Install the requirements
```
pip3 install -r requirements.txt
```
Start the Load Balancer Application
```
venv/bin/gunicorn -b 0.0.0.0:8001 --access-logfile - --chdir $(pwd) "lb_api:create_app()"
```

## Introduction
SDN Load Balancer is instantiated as a VNF on the SDN/NFV platform. Users of the platform are connected to both VLC/mmWave and Wi-Fi Access Networks at the same time, and we assume that they can receive and transmit traffic to any of the two networks, using as default-gateways the Virtual L3 Router inside OpenStack, as shown in Figure below. The default option is to route traffic through the VLC/mmWave Access Network. The Load Balancer uses the Ryu SDN controller in order to monitor the incoming/outgoing traffic at the interface connected to the VLC/mmWave Access Network. Depending on the traffic and the defined upper and lower bitrate limits, the Load Balancer can take one of the following decisions:
•	Route the traffic of a user to the Wi-Fi Access Network, if the monitored traffic is above the upper bitrate limit.
•	Route the traffic of a  user that was connected to the Wi-Fi back to the VLC/mmWave Access Network, if the monitored traffic is below the lower bitrate limit.

![SDN/NFV OpenStack Platform](https://www.dropbox.com/s/au5usu9l0h1lr2z/IoRL-SND_NFV.png?raw=1)

## Initial Parameters
Load Balancer requires some initial operational parameters to be set. These parameters are described in a json file that is called initial_config.json. The template of this file is presented below:
```
{
    "upper_bw_limit": <integer>,
    "lower_bw_limit": <integer>,
    "ryu_ip": <string>,
    "br-int_dpid": <string>,
    "vlc_of_port": <integer>,
    "external_of_port": <integer>,
    "wifi_vlan": <integer>,
    "interval": <integer> 
}
```

| Field        | Description |
| ------------- |---------------|
| upper_bw_limit | The upper bitrate limit [Mbps] |
| lower_bw_limi	| The lower bitrate limit [Mbps] |
| ryu_ip	| The IP of the Ryu controller |
| br-int_dpid	| The dpid of the br-int OVS bridge on OpenStack |
| vlc_of_port	| The OpenFlow port value of the VLC interface on the br-int bridge |
| external_of_port	| The OpenFlow port value of the external interface on the br-int bridge |
| wifi_vlan	| The VLAN used by OpenStack for the Wifi provider network |
| interval	| The time between each Load Balancer traffic measurement [seconds] |


There are two ways to define the initial operational parameters:
1. Use the cloud-init service, adding a cloud-config file, either via the OpenStack, or via the NFV Orchestrator (i.e. Open Source MANO). An example of a cloud-config.yaml file is presented below:
```
#cloud-config
# vim: syntax=yaml
#
write_files:
  - path: /home/iorl/SDN_Load_Balancer/init_config.json
    content: |
      {
        "upper_bw_limit": 40,
        "lower_bw_limit": 20,
        "ryu_ip": "10.100.128.2",
        "br-int_dpid": "182816038959173",
        "vlc_of_port": 12,
          "external_of_port": 2,
        "wifi_vlan": 2,
        "interval": 20
      }
    permissions: "0644"
```
2. Use the North Bound Interface REST API.

## Users
The SDN Load Balancer administrator has to define the list of users that are connected on the IoRL Access Networks. This list matches for each user his/her IP on the Wi-Fi network with his/her IP on the VLC/mmWave network. This is list is a json file given to the Load Balancer via the REST API. The file below presents an example of such list:
```
{
    "users": [
        {
            "vlc_ip": "10.100.131.18",
            "wifi_ip": "10.100.130.56"
        },
        {
            "vlc_ip": "10.100.131.30",
            "wifi_ip": "10.100.130.57"
        },
        {
            "vlc_ip": "10.100.131.31",
            "wifi_ip": "10.100.130.58"
        },
        {
            "vlc_ip": "10.100.131.32",
            "wifi_ip": "10.100.130.59"
        },
        {
            "vlc_ip": "10.100.131.33",
            "wifi_ip": "10.100.130.60"
        },
	{
            "vlc_ip": "10.100.131.34",
            "wifi_ip": "10.100.130.61"
        }
    ]
}
```

## Logs
You can use the SDN Load Balancer NBI REST APIs to retrieve logs of:
•	Load Balancer Logs
•	Service Logs
Both APIs are described in detail in NBI REST API Section

## NBI REST API
For the documentation of the REST APIs, a swagger-ui tool has been integrated to the SDN Load Balancer. Open the http://<load_balancer_IP>:8001/api/docs on a web browser in order to see the swagger page. A screenshot of the swagger-ui is depected in Figure below:
![swagger-ui](https://www.dropbox.com/s/2zkcxcxfxm3yggq/swagger-iorl-lb.JPG?raw=1)

### Logs
| Method        | URI | Data | Description |
| ------------- |---------------| ---------------| ---------------| 
| GET | /api/logs | - | Returns the logs of the Load Balancer Application |

| Method        | URI | Data | Description |
| ------------- |---------------| ---------------| ---------------| 
| GET | /api/service_logs | - | Returns the logs of the Service that implements the Load Balancer Application |

### Initial Operational Parameters
| Method	| URI	| Data	| Description |
| ------------- |---------------| ---------------| ---------------|
| GET	| /api/parameters	| -	| Returns the operational parameters |
| PUT	| /api/parameters	| init_config.json	| Sets the operational parameters |

### Users
| Method	| URI	| Data	| Description |
| ------------- |---------------| ---------------| ---------------|
| GET	| /api/users	| -	| Returns the users list | 
| PUT	| /api/users	| users.json	| Sets the users list | 
| POST	| /api/users	| users.json	| Adds the given users to the existing users list | 
| DELETE	| /api/users	| users.json	| Deletes the given users from the existing users list. If no data are given, the whole users list is deleted | 

### VLC/mmWave users
| Method	| URI	| Data	| Description |
| ------------- |---------------| ---------------| ---------------|
| GET	| /api/vlcusers	| -	| Returns the list of users currently on the VLC/mmWave Access network | 

### Wi-Fi users
| Method	| URI	| Data	| Description |
| ------------- |---------------| ---------------| ---------------|
| GET	| /api/wifiusers	| -	| Returns the list of users currently on the Wi-Fi Access network | 

## Use the SDN Load Balancer VNF
You can download the Load Balancer VNF [here](https://www.dropbox.com/s/08o8fxvkai3ff68/SDN_Load_Balancer.qcow2?dl=0).
Instantiate the VNF on the SDN/NFV platform using the following minimum resources:
•	VCPUs: 2
•	RAM: 2 GB
•	Root Disk: 20 GB
The Load Balancer service should start immediately with the instantiation of the VNF. To verify that the Load Balancer service has started, try the following REST API call:
```
curl http://<load_balancer_IP>:8001/api/logs
```
This should return the logs of the Load Balancer service.

## Run the SDN Load Balancer as a service
Run the make_service script. Note that it will need root privileges
```
./make_service
```
