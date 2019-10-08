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
WS Map is
  b15       vert flip
  b14       horz flip
  b13       tile bank
  b12-b9    palette
  b8-b0     tile 
"""


def main():
    print("map2wsm - {ver}".format(ver=__version__))
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", required=True, type=str, help="Input file")
    parser.add_argument("-o", "--output", type=str, help="Output file", default="output.bin")
    args = parser.parse_args()

    with open(args.input, "rb") as f_in:
        with open(args.output, "wb") as f_out:
            data = f_in.read(4)
            width = struct.unpack("<L", data)[0]
            data = f_in.read(4)
            height = struct.unpack("<L", data)[0]
            print("Width: {w}\nHeight: {h}".format(w=width, h=height))

            for i in range(width * height):
                data = f_in.read(2)
                tmp = struct.unpack("<H", data)[0]
                v_flip = tmp & (1 << 11)
                h_flip = tmp & (1 << 10)
                tile = tmp & 0x1FF
                out = (1 << 15) if v_flip else 0
                out |= (1 << 14) if h_flip else 0
                out |= (tile + 0x2E) & 0xFF
                f_out.write(struct.pack("<H", out))


if __name__ == "__main__":
    main()