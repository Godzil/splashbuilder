"""
Some info.

Size =
    0 = 1BDh
    1 = 3BDh

Tilemap screen1 base = 800h
Tilemap screen2 base = 1000h
Tileset base = 2000h
Sprite base  = 1800h

0000:7000 store the screen orientation
0000:7001 and onward can be used by the boot splash for variables

Splash flags, bit 7 > 0 = 1BPP tiles, 1 = 2BPP tiles
              bit 4-0 store amount of palettes to copy.

For 1bpp tiles, each palettes store 2 colours.
For 2bpp tiles, each palettes store 4 colours.

Splash data is copied at
    0600:0000

Avail color for console name:
          0600:06e6 [0]                0h,   F00h,   F70h,   FF0h
          0600:06ee [4]              7F0h,    F0h,    F7h,    FFh
          0600:06f6 [8]               7Fh,     Fh,   70Fh,   F0Fh
          0600:06fe [12]             F07h,   FFFh,   777h

On the VBlank code,

CS = 0600h
DS = 0600h
ES = ??
SS = 0000h

struct bootsplash_t
{
   uint8_t padding[3];
   uint8_t consoleFlags;
   uint8_t consoleNameColor;
   uint8_t padding2;
   uint8_t size;
   uint8_t startFrame;
   uint8_t endFrame;
   uint8_t spriteCount;
   uint8_t paletteFlags;
   uint8_t tilesCount;
   uint16_t paletteOffset;
   uint16_t tilesetOffset;
   uint16_t tilemapOffset;
   uint16_t horizontalTilemapDestOffset;
   uint16_t verticalTilemapDestOffset;
   uint8_t tilemapWidth;
   uint8_t tilemapHeight;
   uint32_t splashCodePointer;
   uint16_t consoleNameHorizontalPos;
   uint16_t consoleNameVerticalPos;
   uint8_t padding3[2];
   uint16_t soundSampleOffset;
   uint16_t soundChannelDataOffset[3]
};

Sounds seems to be

uint32_t

duration (8 bit) (in vblank)
Volume (8bit)
Pitch (16bit)

if pitch bit 7 is set then the channel is stopped.

"""
import os
import json
import struct
import argparse


class Coordinates(object):
    def __init__(self, config):
        self.x = config["top"]
        self.y = config["left"]


class Animation(object):
    def __init__(self, config):
        self.start = config["startTime"]
        self.end = config["endTime"]


class ConsoleName(object):
    def __init__(self, config):
        self.vertical = Coordinates(config["vertical"])
        self.horizontal = Coordinates(config["horizontal"])
        self.color = config["color"]


class Tiles(object):
    def __init__(self, config):
        self.bpp = config["bpp"]
        self.count = config["count"]
        self.binfile = os.path.abspath(config["binfile"])
        self.data = open(self.binfile, "rb").read()

    def get_size(self):
        return len(self.data)

    def write(self, f):
        f.write(self.data)

class Tilemap(object):
    def __init__(self, config):
        self.vertical = Coordinates(config["vertical"])
        self.horizontal = Coordinates(config["horizontal"])
        self.height = config["height"]
        self.width = config["width"]
        self.binfile = os.path.abspath(config["binfile"])
        self.data = open(self.binfile, "rb").read()

    def get_size(self):
        return len(self.data)

    def get_horz_offset(self):
        return 2 * (self.horizontal.x * 32 + self.horizontal.y) + 0x800

    def get_vert_offset(self):
        return 2 * (self.vertical.x * 32 + self.vertical.y) + 0x800

    def write(self, f):
        f.write(self.data)


class VBlankCode(object):
    def __init__(self, config):
        self.asmfile = os.path.abspath(config["asm"])
        self.binfile = os.path.splitext(self.asmfile)[0] + ".bin"
        runcmd = "nasm -f bin -o {output} {input}".format(input=self.asmfile,
                                                          output=self.binfile)
        os.system(runcmd)
        self.data = open(self.binfile, "rb").read()

    def get_size(self):
        return len(self.data)

    def write(self, f):
        f.write(self.data)


class Sound(object):
    def __init__(self, config):
        self.channelwaves = config["channelwaves"]
        self.waves = open(self.channelwaves, "rb").read()
        self.channeldata = config["channeldata"]
        self.chdata = {}

        self.chdata[0] = None
        self.chdata[1] = None
        self.chdata[2] = None
        self.chdata[3] = None

        if self.channeldata["ch0"] is not "":
            self.chdata[0] = open(self.channeldata["ch0"], "rb").read()
        if self.channeldata["ch1"] is not "":
            self.chdata[1] = open(self.channeldata["ch1"], "rb").read()
        if self.channeldata["ch2"] is not "":
            self.chdata[2] = open(self.channeldata["ch2"], "rb").read()
        if self.channeldata["ch3"] is not "":
            self.chdata[3] = open(self.channeldata["ch3"], "rb").read()

    def get_size(self):
        return len(self.waves)
               #+ len(self.chdata[0]) + len(self.chdata[1]) + \
               #len(self.chdata[2]) + len(self.chdata[3]) + 4 * 2

    def write(self, f):
        f.write(self.waves)


class Palette(object):
    def __init__(self, palette):
        self.palettes = palette["palette"]
        self.bpp = palette["bpp"]
        self.flags = (len(self.palettes) // (2 << self.bpp)) & 0x1F
        if self.bpp == 2:
            self.flags = self.flags | 0x80

    def get_size(self):
        return len(self.palettes) * 2

    def write(self, f):
        for p in self.palettes:
            f.write(struct.pack("BB", p[0], (p[1] << 4) | p[2]))


class BootSplash(object):
    def __init__(self, config_json):
        self._spriteCount = config_json["sprite"]["count"]
        self._animation = Animation(config_json["animation"])
        self._consoleName = ConsoleName(config_json["consoleName"])
        self._palettes = Palette(config_json["palette"])
        self._tiles = Tiles(config_json["tiles"])
        self._tilemap = Tilemap(config_json["tilemap"])
        self._vblankcode = VBlankCode(config_json["vblankCode"])
        self._sound = Sound(config_json["sound"])

        # Set bootsplash, and volume to 2
        self._consoleFlags = 0x82

    def write(self, filename):
        # This is the size of the start structure, used to calculate offset for
        # all other data
        offset = 40
        with open(filename, "wb") as f:
            f.write(struct.pack("xxx"))
            f.write(struct.pack("B", self._consoleFlags))
            f.write(struct.pack("B", self._consoleName.color))
            f.write(struct.pack("x"))
            f.write(struct.pack("B", 1))
            f.write(struct.pack("BB", self._animation.start, self._animation.end))
            f.write(struct.pack("B", self._spriteCount))
            f.write(struct.pack("B", self._palettes.flags)) # Splash flags
            f.write(struct.pack("B", self._tiles.count))
            f.write(struct.pack("<H", offset))  # Palette offset
            print(offset, self._palettes.get_size())
            paletteOffset = offset
            offset += self._palettes.get_size()
            f.write(struct.pack("<H", offset))  # Tileset offset
            print(offset, self._tiles.get_size())
            tilesetOffset = offset
            offset += self._tiles.get_size()
            f.write(struct.pack("<H", offset))  # Tilemap offset
            print(offset, self._tilemap.get_size())
            tilemapOffset = offset
            offset += self._tilemap.get_size()
            f.write(struct.pack("<H", self._tilemap.get_horz_offset()))
            f.write(struct.pack("<H", self._tilemap.get_vert_offset()))
            f.write(struct.pack("B", self._tilemap.width))
            f.write(struct.pack("B", self._tilemap.height))
            f.write(struct.pack("<HH", offset, 0x600))
            print(offset, self._vblankcode.get_size())
            codeOffset = offset
            offset += self._vblankcode.get_size()
            f.write(struct.pack("<BB", self._consoleName.horizontal.x,
                                       self._consoleName.horizontal.y))
            f.write(struct.pack("<BB", self._consoleName.vertical.x,
                                       self._consoleName.vertical.y))
            f.write(struct.pack("xx"))
            f.write(struct.pack("<H", offset))
            print(offset, self._sound.get_size())
            soundWaveOffset = offset
            offset += self._sound.get_size()
            f.write(struct.pack("<H", soundWaveOffset))
            f.write(struct.pack("<H", soundWaveOffset))
            f.write(struct.pack("<H", 0xFFFF))

            self._palettes.write(f)

            self._tiles.write(f)
            self._tilemap.write(f)
            self._vblankcode.write(f)
            self._sound.write(f)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", required=True, type=str, help="Configuration file")
    parser.add_argument("-o", "--output", type=str, help="Output file", default="output.bin")
    args = parser.parse_args()

    try:
        with open(args.config, "rt") as f:
            config = json.load(f)
    except IOError:
        print("Error: config file '{f}' not found".format(f=args.config))
        return -1

    bs = BootSplash(config)
    bs.write(args.output)


if __name__ == "__main__":
    main()