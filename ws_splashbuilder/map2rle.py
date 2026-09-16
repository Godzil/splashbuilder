# Convert GB Map to WS Map
import struct
import argparse

from . import __version__

"""
 GP Map is done:
 - width (4 bytes)
 - height (4 bytes)
 Tiles[] (2 bytes)
  b11   - Vert mirror
  b10   - Horz mirror
  b9-b0 - tile number
"""

"""
RLE format is:
    
    RLE Byte:
    b7 = 1
    b6-b0 = repeat count, if all set mean exit
    
    Non RLE byte:
    b7 = 0
    b6 = Alt pal
    b5 = Y mirror
    b4 = X mirror
    b3 - b0 = tile ID
"""


def main():
    print("map2wsm - {ver}".format(ver=__version__))
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", required=True, type=str, help="Input file")
    parser.add_argument("-o", "--output", type=str, help="Output file", default="output.wsm")
    parser.add_argument("-s", "--skip", type=int, help="Row to skip", default=0)
    parser.add_argument("-f", "--offset", type=int, help="Sprite offset", default=0)
    args = parser.parse_args()

    with open(args.input, "rb") as f_in:
        with open(args.output, "wb") as f_out:
            data = f_in.read(4)
            width = struct.unpack("<L", data)[0]
            data = f_in.read(4)
            height = struct.unpack("<L", data)[0]
            print("Width: {w}\nHeight: {h}".format(w=width, h=height))

            lastByte = -1
            rleCount = 0
            inRle = False

            tmp = struct.pack("B", (args.offset << 4) | args.skip)
            f_out.write(tmp)

            for i in range(width * height):
                data = f_in.read(2)
                if (i / width) >= args.skip:
                    tmp = struct.unpack("<H", data)[0]
                    v_flip = tmp & (1 << 11)
                    h_flip = tmp & (1 << 10)
                    tile = tmp & 0x1FF
                    """
                    b7 = 0
                    b6 = Alt pal
                    b5 = Y mirror
                    b4 = X mirror
                    b3 - b0 = tile ID
                    """
                    if tile > 0:
                        tile -= args.offset

                    out = (1 << 5) if v_flip else 0
                    out |= (1 << 4) if h_flip else 0
                    out |= tile & 0xF

                    if out == lastByte:
                        inRle = True
                        rleCount += 1
                    else:
                        if inRle:
                            tmp = struct.pack("B", 0x80 | rleCount)
                            f_out.write(tmp)
                            inRle = False
                            rleCount = 0

                        tmp = struct.pack("B", out)
                        f_out.write(tmp)

                        lastByte = out
            if inRle and lastByte != 0:
                tmp = struct.pack("B", 0x80 | rleCount)
                f_out.write(tmp)
            tmp = struct.pack("B", 0xFF)
            f_out.write(tmp)





if __name__ == "__main__":
    main()