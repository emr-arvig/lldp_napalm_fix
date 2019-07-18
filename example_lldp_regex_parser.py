import re
import json

output = ("""
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


Total entries displayed: 8""")

sh_lldp = output.splitlines()[5:-3]

lldp = {}

for n in sh_lldp:
    local_interface = n.split()[1]
    if local_interface not in lldp.keys():
        lldp[local_interface] = []

    lldp[local_interface].append(
        {
            "hostname": n.split()[0],
            "port": n.split()[4],
        }
    )

print(json.dumps(lldp, indent=4))

del lldp

lldp = {}

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

print(json.dumps(lldp, indent=4))


'''
def get_lldp_neighbors(self):

    # init result dict
    lldp = {}
    sh_lldp = self.device.show_lldp_neighbors().splitlines()[5:-3]

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
                "hostname": napalm.base.helpers.convert(text_type, hostname),
                "port": napalm.base.helpers.convert(text_type, port),
            }
        )
'''
