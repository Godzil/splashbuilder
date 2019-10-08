# Convert GB CEL to WS Tile
import struct
import argparse
from . import __version__


def main():
    print("cel2wst - {ver}".format(ver=__version__))
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", required=True, type=str, help="Input file")
    parser.add_argument("-o", "--output", type=str, help="Output file", default="output.bin")
    args = parser.parse_args()

    with open(args.input, "rb") as f_in:
        with open(args.output, "wb") as f_out:
            for prout in range(6):
                data = f_in.read(8*8)
                p0 = 0
                p1 = 0

                for y in range(8):
                    for x in range(8):
                        d = struct.unpack("B", data[y*8+x])[0]
                        p0 = p0 << 1
                        p0 |= 1 if d & 0x01 else 0
                        p1 = p1 << 1
                        p1 |= 1 if d & 0x02 else 0
                    f_out.write(struct.pack("BB", p0, p1))
                    p0 = 0
                    p1 = 0


if __name__ == "__main__":
    main()