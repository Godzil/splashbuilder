import struct



with open("channels.bin", "br") as f:
    while True:
        blob = f.read(4)
        data = struct.unpack("<HBB", blob)
        """
        Volume (8bit)
        duration (8 bit) (in vblank)
        Pitch (16bit)
        """
        print("frames count: {dur} - vol: {vol} - pitch: {pitch:X}".format(dur=data[2],
                                                                         vol=data[1],
                                                                         pitch=data[0]))
        if data[0] & 0x8000:
            break

