#!/usr/bin/env python3

"""

PyTCP, Python TCP/IP stack simulation version 0.1 - 2020, Sebastian Majewski
phtx_ether.py - packet handler for outbound Ethernet packets

"""

import ps_ether
import ps_ip


def phtx_ether(self, child_packet, ether_src="00:00:00:00:00:00", ether_dst="00:00:00:00:00:00"):
    """ Handle outbound Ethernet packets """

    ether_packet_tx = ps_ether.EtherPacket(ether_src=ether_src, ether_dst=ether_dst, child_packet=child_packet)

    # Check if packet contains valid source address, fill it out if needed
    if ether_packet_tx.ether_src == "00:00:00:00:00:00":
        ether_packet_tx.ether_src = self.stack_mac_address
        self.logger.debug(f"{ether_packet_tx.tracker} - Set source to stack MAC {ether_packet_tx.ether_src}")

    # Check if packet contains valid destination MAC address
    if ether_packet_tx.ether_dst != "00:00:00:00:00:00":
        self.logger.debug(f"{ether_packet_tx.tracker} - Contains valid destination MAC address")

    # In case packe doesn't contain valid destination MAC address try to obtain it from ARP cache
    elif ether_packet_tx.ether_type == ps_ether.ETHER_TYPE_IP:
        ip_packet_tx = ps_ip.IpPacket(ether_packet_tx)

        mac_address = self.arp_cache.find_entry(ip_packet_tx.ip_dst)
        if mac_address:
            ether_packet_tx.ether_dst = mac_address
            self.logger.debug(f"{ether_packet_tx.tracker} - Resolved destiantion IP {ip_packet_tx.ip_dst} to MAC {ether_packet_tx.ether_dst}")

    # If we not able to obtain valid destination MAC address from the cache then drop packet
    else:
        self.logger.debug(f"{ether_packet_tx.tracker} - Droping packet, no valid destination MAC could be obtained")

    self.logger.debug(f"{ether_packet_tx.tracker} - {ether_packet_tx}")
    self.tx_ring.enqueue(ether_packet_tx, urgent=True if child_packet.protocol == "ARP" else False)