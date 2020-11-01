#!/usr/bin/env python3

"""

PyTCP, Python TCP/IP stack, version 0.1 - 2020, Sebastian Majewski
client_udp_dhcp.py - 'user space' DHCP client

"""

import threading
import random

import udp_socket
import ps_dhcp


class ClientUdpDhcp:
    """ DHCP client support class """

    def __init__(self, stack_mac_address):
        """ Class constructor """

        self.stack_mac_address = stack_mac_address

        self.socket = udp_socket.UdpSocket(local_ip_address="0.0.0.0", local_port=68, remote_ip_address="0.0.0.0", remote_port=67)

        threading.Thread(target=self.__client).start()

    def __client(self):
        """ Obtain IP address from DHCP server """

        dhcp_xid = random.randint(0, 0xFFFFFFFF)

        dhcp_packet_tx = ps_dhcp.DhcpPacket(
            dhcp_xid=dhcp_xid,
            dhcp_chaddr=self.stack_mac_address,
            dhcp_msg_type=ps_dhcp.DHCP_DISCOVER,
            dhcp_param_req_list=b"\x01\x1c\x02\x03\x0f\x06\x77\x0c\x2c\x2f\x1a\x79\x2a",
        )

        self.socket.send_to(
            udp_socket.UdpMessage(
                raw_data=dhcp_packet_tx.get_raw_packet(),
                local_ip_address="0.0.0.0",
                local_port=68,
                remote_ip_address="255.255.255.255",
                remote_port=67,
            )
        )
        print("ClientUdpDhcp: Sent out DHCP Discover message")

        message = self.socket.receive_from()

        dhcp_packet_rx = ps_dhcp.DhcpPacket(message.raw_data)
      
        if dhcp_packet_rx.dhcp_msg_type == ps_dhcp.DHCP_OFFER:
            print(f"ClientUdpDhcp: Received DHCP Offer {dhcp_packet_rx.dhcp_yiaddr} from {message.remote_ip_address}")

        else:
            for option in dhcp_packet_rx.dhcp_options:
                print(option)




