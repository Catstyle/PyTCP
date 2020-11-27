#!/usr/bin/env python3

"""

PyTCP, Python TCP/IP stack, version 0.1 - 2020, Sebastian Majewski
ps_icmpv6.py - protocol support libary for ICMPv6

"""

from ipaddress import IPv6Address, IPv6Network

import struct

import inet_cksum

from tracker import Tracker

import stack


"""

   ICMPv6 packet header - simplified support, only ping echo/reply messages

   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |     Type      |     Code      |           Checksum            |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+


   Destination Unreachable message (1/[0,1,3,4])

   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |              Id               |              Seq              |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |                           Reserved                            |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   ~                             Data                              ~
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+


   Echo Request message (128/0)

   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |              Id               |              Seq              |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   ~                             Data                              ~
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+


   Echo Reply message (129/0)

   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |              Id               |              Seq              |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   ~                             Data                              ~
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+


   Router Solicitation message (133/0)

   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |     Type      |     Code      |          Checksum             |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |                            Reserved                           |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |   Options ...
   +-+-+-+-+-+-+-+-+-+-+-+-

   'Source link-layer address' option
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |       1       |       1       |                               >
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+                               |
   >                           MAC Address                         |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+


   Router Advertisement message (134/0)

   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |     Type      |     Code      |          Checksum             |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |   Hop Limit   |M|O|H|PRF|P|0|0|        Router Lifetime        |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |                          Reachable Time                       |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |                           Retrans Timer                       |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |   Options ...
   +-+-+-+-+-+-+-+-+-+-+-+-

   'Source link-layer address' option
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |       1       |       1       |                               >
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+                               |
   >                           MAC Address                         |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+


   Neighbor Solicitation message (135/0)

   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |     Type      |     Code      |          Checksum             |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |                           Reserved                            |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |                                                               >
   +                                                               +
   >                                                               >
   +                       Target Address                          +
   >                                                               >
   +                                                               +
   >                                                               |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |   Options ...
   +-+-+-+-+-+-+-+-+-+-+-+-

   'Source link-layer address' option
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |       1       |       1       |                               >
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+                               +
   >                           MAC Address                         |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+


   Neighbor Advertisement message (136/0)

   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |     Type      |     Code      |          Checksum             |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |R|S|O|                     Reserved                            |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |                                                               >
   +                                                               +
   >                                                               >
   +                       Target Address                          +
   >                                                               >
   +                                                               +
   >                                                               |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |   Options ...
   +-+-+-+-+-+-+-+-+-+-+-+-

   'Target link-layer address' option
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |       2       |       1       |                               >
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+                               +
   >                           MAC Address                         |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

"""

ICMPV6_HEADER_LEN = 4

ICMPV6_UNREACHABLE = 1
ICMPV6_UNREACHABLE_LEN = 8
ICMPV6_UNREACHABLE_NOROUTE = 0
ICMPV6_UNREACHABLE_PROHIBITED = 1
ICMPV6_UNREACHABLE_ADDRESS = 2
ICMPV6_UNREACHABLE_PORT = 4

ICMPV6_ECHOREQUEST = 128
ICMPV6_ECHOREQUEST_LEN = 4

ICMPV6_ECHOREPLY = 129
ICMPV6_ECHOREPLY_LEN = 4

ICMPV6_ROUTER_SOLICITATION = 133
ICMPV6_ROUTER_SOLICITATION_LEN = 4

ICMPV6_ROUTER_ADVERTISEMENT = 134
ICMPV6_ROUTER_ACVERTISEMENT_LEN = 4

ICMPV6_NEIGHBOR_SOLICITATION = 135
ICMPV6_NEIGHBOR_SOLICITATION_LEN = 4

ICMPV6_NEIGHBOR_ADVERTISEMENT = 136
ICMPV6_NEIGHBOR_ADVERTISEMENT_LEN = 4


class ICMPv6Packet:
    """ ICMPv6 packet support class """

    protocol = "ICMPv6"

    def __init__(
        self,
        parent_packet=None,
        icmpv6_type=None,
        icmpv6_code=0,
        icmpv6_un_raw_data=b"",
        icmpv6_ec_id=None,
        icmpv6_ec_seq=None,
        icmpv6_ec_raw_data=b"",
        icmpv6_ra_hop=None,
        icmpv6_ra_flag_m=False,
        icmpv6_ra_flag_o=False,
        icmpv6_ra_router_lifetime=None,
        icmpv6_ra_reachable_time=None,
        icmpv6_ra_retrans_timer=None,
        icmpv6_ns_target_address=None,
        icmpv6_na_flag_r=False,
        icmpv6_na_flag_s=False,
        icmpv6_na_flag_o=False,
        icmpv6_na_target_address=None,
        icmpv6_nd_options=[],
        echo_tracker=None,
    ):
        """ Class constructor """

        # Packet parsing
        if parent_packet:
            self.tracker = parent_packet.tracker

            raw_message = parent_packet.raw_data

            # from binascii import hexlify
            # print(hexlify(raw_packet))

            self.icmpv6_type = raw_message[0]
            self.icmpv6_code = raw_message[1]
            self.icmpv6_cksum = struct.unpack("!H", raw_message[2:4])[0]

            self.icmpv6_nd_options = []

            if self.icmpv6_type == ICMPV6_UNREACHABLE:
                self.icmpv6_un_reserved = struct.unpack("!L", raw_message[4:8])[0]
                self.icmpv6_un_raw_data = raw_message[8:]
                return

            if self.icmpv6_type == ICMPV6_ECHOREQUEST:
                self.icmpv6_ec_id = struct.unpack("!H", raw_message[4:6])[0]
                self.icmpv6_ec_seq = struct.unpack("!H", raw_message[6:8])[0]
                self.icmpv6_ec_raw_data = raw_message[8:]
                return

            if self.icmpv6_type == ICMPV6_ECHOREPLY:
                self.icmpv6_ec_id = struct.unpack("!H", raw_message[4:6])[0]
                self.icmpv6_ec_seqq = struct.unpack("!H", raw_message[6:8])[0]
                self.icmpv6_ec_raw_data = raw_message[8:]
                return

            if self.icmpv6_type == ICMPV6_ROUTER_SOLICITATION:
                self.icmpv6_rs_reserved = struct.unpack("!L", raw_message[4:8])[0]
                self.icmpv6_nd_options = self.__read_nd_options(raw_message[12:])
                return

            if self.icmpv6_type == ICMPV6_ROUTER_ADVERTISEMENT:
                self.icmpv6_ra_hop = raw_message[4]
                self.icmpv6_ra_flag_m = bool(raw_message[5] & 0b10000000)
                self.icmpv6_ra_flag_o = bool(raw_message[5] & 0b01000000)
                self.icmpv6_ra_reserved = raw_message[5] & 0b00111111
                self.icmpv6_ra_router_lifetime = struct.unpack("!H", raw_message[6:8])[0]
                self.icmpv6_ra_reachable_time = struct.unpack("!L", raw_message[8:12])[0]
                self.icmpv6_ra_retrans_timer = struct.unpack("!L", raw_message[12:16])[0]
                self.icmpv6_nd_options = self.__read_nd_options(raw_message[16:])
                return

            if self.icmpv6_type == ICMPV6_NEIGHBOR_SOLICITATION:
                self.icmpv6_ns_reserved = struct.unpack("!L", raw_message[4:8])[0]
                self.icmpv6_ns_target_address = IPv6Address(raw_message[8:24])
                self.icmpv6_nd_options = self.__read_nd_options(raw_message[24:])
                return

            if self.icmpv6_type == ICMPV6_NEIGHBOR_ADVERTISEMENT:
                self.icmpv6_na_flag_r = bool(raw_message[4] & 0b10000000)
                self.icmpv6_na_flag_s = bool(raw_message[4] & 0b01000000)
                self.icmpv6_na_flag_o = bool(raw_message[4] & 0b00100000)
                self.icmpv6_na_reserved = struct.unpack("!L", raw_message[4:8])[0] & 0b00011111111111111111111111111111
                self.icmpv6_na_target_address = IPv6Address(raw_message[4:20])
                self.icmpv6_nd_options = self.__read_nd_options(raw_message[20:])
                return

        # Packet building
        else:
            self.tracker = Tracker("TX", echo_tracker)

            self.icmpv6_type = icmpv6_type
            self.icmpv6_code = icmpv6_code
            self.icmpv6_cksum = 0

            self.icmpv6_nd_options = icmpv6_nd_options

            if self.icmpv6_type == ICMPV6_UNREACHABLE:
                self.icmpv6_un_reserved = 0
                self.icmpv6_un_raw_data = icmpv6_un_raw_data[:520]
                return

            if self.icmpv6_type == ICMPV6_ECHOREQUEST and self.icmpv6_code == 0:
                self.icmpv6_ec_id = icmpv6_ec_id
                self.icmpv6_ec_seq = icmpv6_ec_seq
                self.icmpv6_ec_raw_data = icmpv6_ec_raw_data
                return

            if self.icmpv6_type == ICMPV6_ECHOREPLY and self.icmpv6_code == 0:
                self.icmpv6_ec_id = icmpv6_ec_id
                self.icmpv6_ec_seq = icmpv6_ec_seq
                self.icmpv6_ec_raw_data = icmpv6_ec_raw_data
                return

            if self.icmpv6_type == ICMPV6_ROUTER_SOLICITATION:
                self.icmpv6_rs_reserved = 0
                return

            if self.icmpv6_type == ICMPV6_ROUTER_ADVERTISEMENT:
                self.icmpv6_ra_hop = icmpv6_ra_hop
                self.icmpv6_ra_flag_m = icmpv6_ra_flag_m
                self.icmpv6_ra_flag_o = icmpv6_ra_flag_o
                self.icmpv6_ra_router_lifetime = icmpv6_ra_router_lifetime
                self.icmpv6_ra_reachable_time = icmpv6_ra_reachable_time
                self.icmpv6_ra_retrans_timer = icmpv6_ra_retrans_timer
                return

            if self.icmpv6_type == ICMPV6_NEIGHBOR_SOLICITATION:
                self.icmpv6_ns_reserved = 0
                self.icmpv6_ns_target_address = icmpv6_ns_target_address
                return

            if self.icmpv6_type == ICMPV6_NEIGHBOR_ADVERTISEMENT:
                self.icmpv6_na_flag_r = icmpv6_na_flag_r
                self.icmpv6_na_flag_s = icmpv6_na_flag_s
                self.icmpv6_na_flag_o = icmpv6_na_flag_o
                self.icmpv6_na_reserved = 0
                self.icmpv6_na_target_address = icmpv6_na_target_address
                return

    def __str__(self):
        """ Short packet log string """

        log = f"ICMPv6 type {self.icmpv6_type}, code {self.icmpv6_code}"

        if self.icmpv6_type == ICMPV6_UNREACHABLE:
            pass

        if self.icmpv6_type == ICMPV6_ECHOREQUEST:
            log += f", id {self.icmpv6_ec_id}, seq {self.icmpv6_ec_seq}"

        if self.icmpv6_type == ICMPV6_ECHOREPLY:
            log += f", id {self.icmpv6_ec_id}, seq {self.icmpv6_ec_seq}"

        if self.icmpv6_type == ICMPV6_ROUTER_SOLICITATION:
            pass

        if self.icmpv6_type == ICMPV6_ROUTER_ADVERTISEMENT:
            log += f", hop {self.icmpv6_ra_hop}"
            log += f"flags {'M' if self.icmpv6_ra_flag_m else '-'}{'O' if self.icmpv6_ra_flag_o else '-'}"
            log += f"rlft {self.icmpv6_ra_router_lifetime}, reacht {self.icmpv6_ra_reachable_time}, retrt {self.icmpv6_ra_retrans_timer}"

        if self.icmpv6_type == ICMPV6_NEIGHBOR_SOLICITATION:
            log += f", target {self.icmpv6_ns_target_address}"

        if self.icmpv6_type == ICMPV6_NEIGHBOR_ADVERTISEMENT:
            log += f", target {self.icmpv6_na_target_address}"
            log += f", flags {'R' if self.icmpv6_na_flag_r else '-'}{'S' if self.icmpv6_na_flag_s else '-'}{'O' if self.icmpv6_na_flag_o else '-'}"

        for nd_option in self.icmpv6_nd_options:
            log += ", " + str(nd_option)

        return log

    def __len__(self):
        """ Length of the packet """

        return len(self.raw_packet)

    @property
    def raw_message(self):
        """ Get packet message in raw format """

        if self.icmpv6_type == ICMPV6_UNREACHABLE:
            return (
                struct.pack("! BBH HH", self.icmpv6_type, self.icmpv6_code, self.icmpv6_cksum, self.icmv6_un_reserved, stack.mtu if self.code == 4 else 0)
                + self.icmpv6_un_raw_data
            )

        if self.icmpv6_type == ICMPV6_ECHOREQUEST:
            return (
                struct.pack("! BBH HH", self.icmpv6_type, self.icmpv6_code, self.icmpv6_cksum, self.icmpv6_ec_id, self.icmpv6_ec_seq) + self.icmpv6_ec_raw_data
            )

        if self.icmpv6_type == ICMPV6_ECHOREPLY:
            return (
                struct.pack("! BBH HH", self.icmpv6_type, self.icmpv6_code, self.icmpv6_cksum, self.icmpv6_ec_id, self.icmpv6_ec_seq) + self.icmpv6_ec_raw_data
            )

        if self.icmpv6_type == ICMPV6_ROUTER_SOLICITATION:
            return struct.pack("! BBH L", self.icmpv6_type, self.icmpv6_code, self.icmpv6_cksum, self.icmpv6_rs_reserved) + self.raw_nd_options

        if self.icmpv6_type == ICMPV6_ROUTER_ADVERTISEMENT:
            return (
                struct.pack(
                    "! BBH BBH L L",
                    self.icmpv6_type,
                    self.icmpv6_code,
                    self.icmpv6_cksum,
                    self.icmpv6_ra_hop,
                    (self.icmpv6_ra_flag_m << 7) | (self.icmpv6_ra_flag_o << 6) | self.icmpv6_ra_reserved,
                    self.icmpv6_ra_reachable_time,
                    self.icmpv6_ra_retrans_timer,
                )
                + self.raw_nd_options
            )

        if self.icmpv6_type == ICMPV6_NEIGHBOR_SOLICITATION:
            return (
                struct.pack(
                    "! BBH L 16s",
                    self.icmpv6_type,
                    self.icmpv6_code,
                    self.icmpv6_cksum,
                    self.icmpv6_ns_reserved,
                    self.icmpv6_ns_target_address.packed,
                )
                + self.raw_nd_options
            )

        if self.icmpv6_type == ICMPV6_NEIGHBOR_ADVERTISEMENT:
            return (
                struct.pack(
                    "! BBH L 16s",
                    self.icmpv6_type,
                    self.icmpv6_code,
                    self.icmpv6_cksum,
                    (self.icmpv6_na_flag_r << 31) | (self.icmpv6_na_flag_s << 30) | (self.icmpv6_na_flag_o << 29) | self.icmpv6_na_reserved,
                    self.icmpv6_na_target_address.packed,
                )
                + self.raw_nd_options
            )

    @property
    def raw_packet(self):
        """ Get packet in raw format """

        return self.raw_message

    def get_raw_packet(self, ip_pseudo_header):
        """ Get packet in raw format ready to be processed by lower level protocol """

        self.icmpv6_cksum = inet_cksum.compute_cksum(ip_pseudo_header + self.raw_packet)

        return self.raw_packet

    @property
    def raw_nd_options(self):
        """ ICMPv6 ND packet options in raw format """

        raw_nd_options = b""

        for option in self.icmpv6_nd_options:
            raw_nd_options += option.raw_option

        return raw_nd_options

    def validate_cksum(self, ip_pseudo_header):
        """ Validate packet checksum """

        # from binascii import hexlify
        # print(hexlify(self.raw_packet))

        return not bool(inet_cksum.compute_cksum(ip_pseudo_header + self.raw_packet))

    def __read_nd_options(self, raw_nd_options):
        """ Read options for Neighbor Discovery """

        opt_cls = {
            ICMPV6_ND_OPT_SLLA: ICMPv6NdOptSLLA,
            ICMPV6_ND_OPT_TLLA: ICMPv6NdOptTLLA,
        }

        i = 0
        nd_options = []

        while i < len(raw_nd_options):
            nd_options.append(opt_cls.get(raw_nd_options[i], ICMPv6NdOptUnk)(raw_nd_options[i : i + (raw_nd_options[i + 1] << 3)]))
            i += raw_nd_options[i + 1] << 3

        return nd_options

    @property
    def icmpv6_nd_opt_slla(self):
        """ ICMPv6 ND option - Source Link Layer Address (1) """

        for option in self.icmpv6_nd_options:
            if option.opt_code == ICMPV6_ND_OPT_SLLA:
                return option.opt_slla

    @property
    def icmpv6_nd_opt_tlla(self):
        """ ICMPv6 ND option - Target Link Layer Address (2) """

        for option in self.icmpv6_nd_options:
            if option.opt_code == ICMPV6_ND_OPT_TLLA:
                return option.opt_tlla


"""

    ICMPv6 Neighbor Discovery options

"""

# ICMPv6 ND option - Source Link Layer Address (1)

ICMPV6_ND_OPT_SLLA = 1
ICMPV6_ND_OPT_SLLA_LEN = 8


class ICMPv6NdOptSLLA:
    """ ICMPv6 ND option - Source Link Layer Address (1) """

    def __init__(self, raw_option=None, opt_slla=None):
        if raw_option:
            self.opt_code = raw_option[0]
            self.opt_len = raw_option[1] << 3
            self.opt_slla = ":".join([f"{_:0>2x}" for _ in raw_option[2:8]])
        else:
            self.opt_code = ICMPV6_ND_OPT_SLLA
            self.opt_len = ICMPV6_ND_OPT_SLLA_LEN
            self.opt_slla = opt_slla

    @property
    def raw_option(self):
        return struct.pack("! BB 6s", self.opt_code, self.opt_len >> 3, bytes.fromhex(self.opt_slla.replace(":", "")))

    def __str__(self):
        return f"slla {self.opt_slla}"


# ICMPv6 ND option - Target Link Layer Address (2)

ICMPV6_ND_OPT_TLLA = 2
ICMPV6_ND_OPT_TLLA_LEN = 8


class ICMPv6NdOptTLLA:
    """ ICMPv6 ND option - Target Link Layer Address (2) """

    def __init__(self, raw_option=None, opt_tlla=None):
        if raw_option:
            self.opt_code = raw_option[0]
            self.opt_len = raw_option[1] << 3
            self.opt_tlla = ":".join([f"{_:0>2x}" for _ in raw_option[2:8]])
        else:
            self.opt_code = ICMPV6_ND_OPT_TLLA
            self.opt_len = ICMPV6_ND_OPT_TLLA_LEN
            self.opt_tlla = opt_tlla

    @property
    def raw_option(self):
        return struct.pack("! BB 6s", self.opt_code, self.opt_len >> 3, bytes.fromhex(self.opt_tlla.replace(":", "")))

    def __str__(self):
        return f"tlla {self.opt_tlla}"


# ICMPv6 ND option - Prefix Information (3)

ICMPV6_ND_OPT_PI = 3
ICMPV6_ND_OPT_PI_LEN = 32


class ICMPv6NdOptPI:
    """ ICMPv6 ND option - Prefix Information (3) """

    def __init__(
        self,
        raw_option=None,
        opt_flag_o=False,
        opt_flag_a=False,
        opt_flag_r=False,
        opt_valid_lifetime=None,
        opt_preferred_lifetime=None,
        opt_prefix=None,
    ):
        if raw_option:
            self.opt_code = raw_option[0]
            self.opt_len = raw_option[1] << 3
            self.opt_flag_o = bool(raw_option[3] & 0b10000000)
            self.opt_flag_a = bool(raw_option[3] & 0b01000000)
            self.opt_flag_r = bool(raw_option[3] & 0b00100000)
            self.opt_reserved_1 = raw_option[3] & 0b00011111
            self.opt_valid_lifetime = struct.unpack("!L", raw_option[4:8])[0]
            self.opt_preferred_lifetime = struct.unpack("!L", raw_option[8:12])[0]
            self.opt_reserved_2 = struct.unpack("!L", raw_option[12:16])[0]
            self.opt_prefix = IPv6Network((raw_option[16:32], raw_option[2]))
        else:
            self.opt_code = ICMPV6_ND_OPT_PI
            self.opt_len = ICMPV6_ND_OPT_PI_LEN
            self.opt_flag_o = opt_flag_o
            self.opt_flag_a = opt_flag_a
            self.opt_flag_r = opt_flag_r
            self.opt_reserved_1 = 0
            self.opt_valid_lifetime = opt_valid_lifetime
            self.opt_valid_preferred = opt_preferred_lifetime
            self.opt_reserved_2 = 0
            self.opt_prefix = IPv6Network(opt_prefix)

    @property
    def raw_option(self):
        return struct.pack(
            "! BB BB L L 16s",
            self.opt_code,
            self.opt_len >> 3,
            self.opt_prefix.prefixlen,
            (self.opt_flag_o << 7) | (self.opt_flag_a << 6) | (self.opt_flag_r << 6) | self.opt_reserved_1,
            self.opt_valid_lifetime,
            self.opt_preferred_lifetime,
            self.opt_reserved_2,
            self.opt_prefix.network_address.packed,
        )

    def __str__(self):
        return f"prefix_info {self.opt_prefix}"


# ICMPv6 ND option not supported by this stack


class ICMPv6NdOptUnk:
    """ ICMPv6 ND  option not supported by this stack """

    def __init__(self, raw_option):
        self.opt_code = raw_option[0]
        self.opt_len = raw_option[1] << 3
        self.opt_data = raw_option[2 : self.opt_len]

    @property
    def raw_option(self):
        return struct.pack("! BB", self.opt_code, self.opt_len >> 3) + self.opt_data

    def __str__(self):
        return "unk"
