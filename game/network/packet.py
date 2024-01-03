import struct
import pickle


class PACKETS:
    C2S_HELLO = 1
    C2S_POSITION_UPDATE = 2
    S2C_FULL_UPDATE = 3
    S2C_POSITION_UPDATE = 4
    S2C_HELLO = 5


class Packet:
    MAGIC = b'NPACKET'
    MAGIC_SIZE = len(MAGIC)
    STRUCT_PACKET = f"{MAGIC_SIZE}sII"
    HEADER_SIZE = struct.calcsize(STRUCT_PACKET)

    def __init__(self, packet_id=None, data=None):
        self.packet_id = packet_id
        self.data = data

    def pack(self):
        data_bytes = pickle.dumps(self.data)
        header = struct.pack(Packet.STRUCT_PACKET, self.MAGIC, self.packet_id, len(data_bytes))
        return header + data_bytes

    @staticmethod
    def unpack_header(header):
        magic, packet_id, packet_size = struct.unpack(Packet.STRUCT_PACKET, header)
        if magic != Packet.MAGIC:
            raise ValueError('Packet magic mismatch')
        return magic, packet_id, packet_size

    @staticmethod
    def unpack(header, data_bytes):
        data = pickle.loads(data_bytes)
        return Packet(packet_id=header[1], data=data)
