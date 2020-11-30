#!/usr/bin/env python3

############################################################################
#                                                                          #
#  PyTCP - Python TCP/IP stack                                             #
#  Copyright (C) 2020  Sebastian Majewski                                  #
#                                                                          #
#  This program is free software: you can redistribute it and/or modify    #
#  it under the terms of the GNU General Public License as published by    #
#  the Free Software Foundation, either version 3 of the License, or       #
#  (at your option) any later version.                                     #
#                                                                          #
#  This program is distributed in the hope that it will be useful,         #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of          #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the           #
#  GNU General Public License for more details.                            #
#                                                                          #
#  You should have received a copy of the GNU General Public License       #
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.  #
#                                                                          #
#  Author's email: ccie18643@gmail.com                                     #
#  Github repository: https://github.com/ccie18643/PyTCP                   #
#                                                                          #
############################################################################

##############################################################################################
#                                                                                            #
#  This program is a work in progress and it changes on daily basis due to new features      #
#  being implemented, changes being made to already implemented features, bug fixes, etc.    #
#  Therefore if the current version is not working as expected try to clone it again the     #
#  next day or shoot me an email describing the problem. Any input is appreciated. Also      #
#  keep in mind that some features may be implemented only partially (as needed for stack    #
#  operation) or they may be implemented in sub-optimal or not 100% RFC compliant way (due   #
#  to lack of time) or last but not least they may contain bug(s) that i didn't notice yet.  #
#                                                                                            #
##############################################################################################


#
# phtx_ip6.py - packet handler for outbound IPv6 packets
#


from ipaddress import IPv6Address

import ps_ip6
import stack


def validate_src_ip6_address(self, ip6_src):
    """ Make sure source ip address is valid, supplemt with valid one as appropriate """

    # Check if the the source IP address belongs to this stack or its set to all zeros (for ND DAD)
    if ip6_src not in {*self.stack_ip6_unicast, *self.stack_ip6_multicast, IPv6Address("::")}:
        self.logger.warning(f"Unable to sent out IPv6 packet, stack doesn't own IPv6 address {ip6_src}")
        return None

    # If packet is a response to multicast then replace source IPv6 address with link local IPv6 address of the stack
    if ip6_src in self.stack_ip6_multicast:
        if self.stack_ip6_unicast:
            ip6_src = self.stack_ip6_unicast[0]
            self.logger.debug(f"Packet is response to multicast, replaced source with stack link local IPv6 address {ip6_src}")
        else:
            self.logger.warning("Unable to sent out IPv6 packet, no stack link local unicast IPv6 address available")
            return None

    # If packet is a response to All IPv6 Nodes multicast then replace source IPv6 address with link local IPv6 address of the stack
    if ip6_src == IPv6Address("ff02::1"):
        if self.stack_ip6_unicast:
            ip6_src = self.stack_ip6_unicast[0]
            self.logger.debug(f"Packet is response to All IPv6 Nodes multicast, replaced source with stack link local IPv6 address {ip6_src}")
        else:
            self.logger.warning("Unable to sent out IPv6 packet, no stack link local unicast IP address available")
            return None

    return ip6_src


def validate_dst_ip6_address(ip6_dst):
    """ Make sure destination ip address is valid, supplemt with valid one as appropriate """

    # Check if destiantion address is all zeroes, substitute it with All IPv6 Nodes multicast address
    if ip6_dst.is_unspecified:
        ip6_dst = IPv6Address("ff02::1")

    return ip6_dst


def phtx_ip6(self, child_packet, ip6_dst, ip6_src, ip6_hop=64):
    """ Handle outbound IP packets """

    # Check if IPv6 protocol support is enabled, if not then silently drop the packet
    if not stack.ip6_support:
        return

    # Make sure source and destination addresses are the right object type
    ip6_src = IPv6Address(ip6_src)
    ip6_dst = IPv6Address(ip6_dst)

    # Validate source address
    ip6_src = validate_src_ip6_address(self, ip6_src)
    if not ip6_src:
        return

    # Validate destination address
    ip6_dst = validate_dst_ip6_address(ip6_dst)
    if not ip6_dst:
        return

    # Check if IP packet can be sent out without fragmentation, if so send it out
    if ps_ip6.IP6_HEADER_LEN + len(child_packet.raw_packet) <= stack.mtu:
        ip6_packet_tx = ps_ip6.Ip6Packet(ip6_src=ip6_src, ip6_dst=ip6_dst, ip6_hop=ip6_hop, child_packet=child_packet)

        self.logger.debug(f"{ip6_packet_tx.tracker} - {ip6_packet_tx}")
        self.phtx_ether(child_packet=ip6_packet_tx)
        return

    # Fragment packet and send all fragments out *** Need to add this functionality ***
    self.logger.debug("Packet exceedes available MTU, IPv6 fragmentation needed... droping...")
    return