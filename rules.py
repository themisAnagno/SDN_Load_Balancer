to_wifi_rule = {
    "dpid": "182816038959173",
    "table_id": "0",
    "priority": "80",
    "match": {
        "eth_type": 2048,
        "ipv4_dst": "10.100.131.13",
        "dl_vlan": "0x0000",
        "in_port": 2
    },
    "actions": [
                {
                    "type": "PUSH_VLAN",
                    "ethertype": 33024
                },
                {
                    "type": "SET_FIELD",
                    "field": "vlan_vid",
                    "value": 4098
                },
                {
                    "type": "SET_FIELD",
                    "field": "ipv4_dst",
                    "value": "10.100.130.13"
                },
                {
                    "type": "GOTO_TABLE",
                    "table_id": 60
                }
            ]
}
