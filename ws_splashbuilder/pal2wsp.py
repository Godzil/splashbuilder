# Convert ProMotion PAL to WS Palette
import struct
import argparse
from . import __version__


def main():
    print("pal2wsp - {ver}".format(ver=__version__))
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", required=True, type=str, help="Input file")
    parser.add_argument("-o", "--output", type=str, help="Output file", default="output.wsp")
    args = parser.parse_args()

    with open(args.input, "rb") as f_in:
        with open(args.output, "wb") as f_out:
            # 16 colours, 16 palettes
            for currentPaletteEntry in range(16 * 16):
                dataIn = f_in.read(2)
                palette = struct.unpack("<H", dataIn)[0]

                red = (palette & 0x7C00) >> 10
                green = (palette & 0x03E0) >> 5
                blue = (palette & 0x1F)

                red = int((red * 16) / 32.)
                green = int((green * 16) / 32.)
                blue = int((blue * 16) / 32.)

                print(f"[ {red}, {green}, {blue}] ,", end="")

                newvalue = (blue << 8) | (green << 4) | red
                data = struct.pack("<H", newvalue)
                f_out.write(data)

if __name__ == "__main__":
    main()