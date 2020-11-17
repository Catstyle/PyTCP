#!/usr/bin/env python3

"""

PyTCP, Python TCP/IP stack, version 0.1 - 2020, Sebastian Majewski
tcp_packet.py - module contains storage class for incoming TCP packet's metadata

"""


class TcpPacketMetadata:
    """ Store TCP metadata """

    def __init__(
        self,
        local_ip_address,
        local_port,
        remote_ip_address,
        remote_port,
        flag_syn,
        flag_ack,
        flag_fin,
        flag_rst,
        seq,
        ack,
        win,
        wscale,
        mss,
        raw_data,
        tracker,
    ):
        self.local_ip_address = local_ip_address
        self.local_port = local_port
        self.remote_ip_address = remote_ip_address
        self.remote_port = remote_port
        self.flag_syn = flag_syn
        self.flag_ack = flag_ack
        self.flag_fin = flag_fin
        self.flag_rst = flag_rst
        self.seq = seq
        self.ack = ack
        self.win = win
        self.wscale = wscale
        self.mss = mss
        self.raw_data = raw_data
        self.tracker = tracker

    @property
    def tcp_session_id(self):
        """ Session ID """

        return f"TCP/{self.local_ip_address}/{self.local_port}/{self.remote_ip_address}/{self.remote_port}"

    @property
    def tcp_session_listening_patterns(self):
        """ Session ID patterns that match listening socket """

        return [
            f"TCP/{self.local_ip_address}/{self.local_port}/0.0.0.0/0",
            f"TCP/0.0.0.0/{self.local_port}/0.0.0.0/0",
        ]