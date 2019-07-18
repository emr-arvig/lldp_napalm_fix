# IOSXR driver LLDP output invalid with spaces in names

Napalm IOSXRDriver method `get_lldp_neighbors()` is having a bit of trouble parsing LLDP in our environment when there are spaces in either the local interface or the remote port description. When there are spaces in the Device ID, they key is incorrect. When there are spaces in the remote port ID name we get incomplete information.

# Sample pseudo-router output


    Capability codes:
            (R) Router, (B) Bridge, (T) Telephone, (C) DOCSIS Cable Device
            (W) WLAN Access Point, (P) Repeater, (S) Station, (O) Other
    
    Device ID       Local Intf          Hold-time  Capability     Port ID
    test1-device-no-spaces-1.domain.net          Te0/0/0/0            120       R          Te0/0/2/1
    test2-device-no-spaces-2.net                 Te0/0/0/2            120       R          BE51
    test3 device with space 1.domain.net         Gi200/0/0/0          40        B          1/g1
    test4 device with space 2.domain.net         Gi200/0/0/11         40        B          1/g1
    device5.domain.net                           Gi200/0/0/16         121       N/A        REMOTE-DEVICE-PORT-HAS-NO-SPACES
    device6.domain.net                           Gi200/0/0/17         121       N/A        REMOTE DEVICE PORT HAS SPACES
    test7 device with spaces.domain.net          Gi200/0/0/18         121       N/A        REMOTE-DEVICE-PORT-HAS-NO-SPACES
    test8 device with spaces.domain.net          Gi200/0/0/19         121       N/A        REMOTE DEVICE PORT HAS SPACES


## json output from napalm:

    {
        "device": [
            {
                "hostname": "test3",
                "port": "1.domain.net"
            },
            {
                "hostname": "test4",
                "port": "2.domain.net"
            },
            {
                "hostname": "test7",
                "port": "Gi200/0/0/18"
            },
            {
                "hostname": "test8",
                "port": "Gi200/0/0/19"
            }
        ],
        "Te0/0/0/2": [
            {
                "hostname": "test2-device-no-spaces-2.net",
                "port": "BE51"
            }
        ],
        "Te0/0/0/0": [
            {
                "hostname": "test1-device-no-spaces-1.domain.net",
                "port": "Te0/0/2/1"
            }
        ],
        "Gi200/0/0/16": [
            {
                "hostname": "device5.domain.net",
                "port": "REMOTE-DEVICE-PORT-HAS-NO-SPACES"
            }
        ],
        "Gi200/0/0/17": [
            {
                "hostname": "device6.domain.net",
                "port": "REMOTE"
            }
        ]
    }


## Problem

The problem comes from using `split()` since obviously that is going to split the string on any spaces we find. 

## Potential solution(s)

I did a quick and dirty hack by using `re.split()` on [782](https://github.com/napalm-automation/napalm/blob/55dffe0233f522724c9b59ab9661212f62254932/napalm/iosxr/iosxr.py#L782), [788](https://github.com/napalm-automation/napalm/blob/55dffe0233f522724c9b59ab9661212f62254932/napalm/iosxr/iosxr.py#L788) and [789](https://github.com/napalm-automation/napalm/blob/55dffe0233f522724c9b59ab9661212f62254932/napalm/iosxr/iosxr.py#L789) instead of `split()[i]`:

    re.split('\s\s+', n)

This isn't the *best* way to do it since again if there is more than one space it will also fail.

I hate adding regex as much as the next person but this was what was the most reliable for me in testing:

    for n in sh_lldp:
        data = re.match('(^.+?\s+)((Gi\d{0,3}|Te\d|Hu\d)(\/[0-9]{0,4})+)\s+\d{2,3}\s+.{1,3}\s+(.+)', n)
        if not data:
            continue
        data_groups = data.groups()
        hostname = data_groups[0].strip()
        local_interface = data_groups[1].strip()
        port = data_groups[4].strip()
        if local_interface not in lldp.keys():
            lldp[local_interface] = []
        lldp[local_interface].append(
            {
                "hostname": hostname,
                "port": port,
            }
        )

**json output:**

    {
        "Gi200/0/0/16": [
            {
                "hostname": "device5.domain.net",
                "port": "REMOTE-DEVICE-PORT-HAS-NO-SPACES"
            }
        ],
        "Gi200/0/0/17": [
            {
                "hostname": "device6.domain.net",
                "port": "REMOTE DEVICE PORT HAS SPACES"
            }
        ],
        "Gi200/0/0/11": [
            {
                "hostname": "test4 device with space 2.domain.net",
                "port": "1/g1"
            }
        ],
        "Te0/0/0/2": [
            {
                "hostname": "test2-device-no-spaces-2.net",
                "port": "BE51"
            }
        ],
        "Te0/0/0/0": [
            {
                "hostname": "test1-device-no-spaces-1.domain.net",
                "port": "Te0/0/2/1"
            }
        ],
        "Gi200/0/0/18": [
            {
                "hostname": "test7 device with spaces.domain.net",
                "port": "REMOTE-DEVICE-PORT-HAS-NO-SPACES"
            }
        ],
        "Gi200/0/0/19": [
            {
                "hostname": "test8 device with spaces.domain.net",
                "port": "REMOTE DEVICE PORT HAS SPACES"
            }
        ],
        "Gi200/0/0/0": [
            {
                "hostname": "test3 device with space 1.domain.net",
                "port": "1/g1"
            }
        ]
    }

There may be a better more pythonic way of doing this - I am by no means a python or regex expert but this is what we are using for now as a shim. I have tested this using the output from a handful of IOSXR routers we have and it has applied successfully to all of them.

The reason we needed to do this was essentially to get Netbox up and running and we were unable to use the LLDP connection methods without either sorting this out in Napalm or running through and fixing all the local and remote ports in our network (and, being an ISP, we only have access to a limited number of remote devices to make changes anyway). 

Thank you! 
