def to_wifi(params, user):

    to_wifi_data = {
        "dpid": int(params["br-int_dpid"]),
        "table_id": 0,
        "priority": 80,
        "idle_timeout": 120,
        "match": {
            "eth_type": 2048,
            "ipv4_dst": user["vlc_ip"],
            "dl_vlan": "0x0000",
            "in_port": params["external_of_port"]
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
                        "value": user["wifi_ip"]
                    },
                    {
                        "type": "GOTO_TABLE",
                        "table_id": 60
                    }
                ]
        }

    return to_wifi_data


def from_wifi(params, user):

    from_wifi_data = {
        "dpid": int(params["br-int_dpid"]),
        "table_id": 0,
        "priority": 2,
        "idle_timeout": 120,
        "match": {
            "eth_type": 2048,
            "ipv4_src": user["wifi_ip"]
        },
        "actions": [
                    {
                        "type": "SET_FIELD",
                        "field": "ipv4_src",
                        "value": user["vlc_ip"]
                    },
                    {
                        "type": "GOTO_TABLE",
                        "table_id": 60
                    }
                ]
        }

    return from_wifi_data
