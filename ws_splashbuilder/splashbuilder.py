import os
import json
import struct
import argparse
from . import __version__


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
        binfile = os.path.abspath(config["binfile"])
        self.data = open(binfile, "rb").read()

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

        binfile = os.path.abspath(config["binfile"])
        self.data = open(binfile, "rb").read()

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
        if "asm" in config:
            asmfile = os.path.abspath(config["asm"])
            binfile = os.path.splitext(asmfile)[0] + ".bin"
            runcmd = "nasm -f bin -o {output} {input}".format(input=asmfile,
                                                              output=binfile)
            os.system(runcmd)
            self.data = open(binfile, "rb").read()
        elif "binfile" in config:
            binfile = os.path.abspath(config["binfile"])
            self.data = open(binfile, "rb").read()
        else:
            self.data = b"cb"

    def get_size(self):
        return len(self.data)

    def write(self, f):
        f.write(self.data)


class Sound(object):
    def __init__(self, config):
        binfile = os.path.abspath(config["waves"])
        self.waves = open(binfile, "rb").read()

        channeldata = config["channelbin"]
        self.chdata = {}

        self.channel_count = 0

        for i in range(4):
            self.chdata[i] = None
            tag = "ch{i}".format(i=i)
            if channeldata[tag] is not "":
                self.channel_count += 1
                binfile = os.path.abspath(channeldata[tag])
                self.chdata[i] = open(binfile, "rb").read()

        if self.channel_count == 0:
            raise Exception("You need at least one channel")

    def get_size(self):
        return len(self.waves)

    def get_ch_size(self):
        current_len = 0
        for i in range(4):
            if self.chdata[i]:
                current_len += len(self.chdata[i])

        return current_len

    def get_list_size(self):
        current_len = 2  # We always have a tag to show the end of list
        for i in range(4):
            if self.chdata[i]:
                current_len += 2

        return current_len

    def write(self, f):
        f.write(self.waves)

    def write_list(self, f, offset):
        for i in range(4):
            if self.chdata[i]:
                f.write(struct.pack("<H", offset))
                offset += len(self.chdata[i])

        # End of list tag
        f.write(struct.pack("BB", 0xFF, 0xFF))

    def write_ch(self, f):
        for i in range(4):
            if self.chdata[i]:
                f.write(self.chdata[i])


class Palette(object):
    def __init__(self, config):
        if "palette" in config:
            self.palettes = config["palette"]
            self.data = None
        elif "binfile" in config:
            self.palettes = None
            self.data = open(config["binfile"], "rb").read()
        else:
            self.data = b""

        self.bpp = config["bpp"]

        if self.palettes:
            self.flags = (len(self.palettes) / (1 << self.bpp))
        else:
            self.flags = ((len(self.data) / 2) / (1 << self.bpp))

        if int(self.flags) != self.flags:
            raise Exception("You palette length don't match with the chosen BPP")
        if self.flags > 16:
            raise Exception("You have too many palettes set (max 16)")

        self.flags = int(self.flags) & 0x1F

        if self.bpp == 2:
            self.flags = self.flags | 0x80
        else:
            self.flags = self.flags & ~0x80

    def get_size(self):
        return len(self.palettes) * 2

    def write(self, f):
        if self.palettes:
            for p in self.palettes:
                f.write(struct.pack("BB", (p[1] << 4) | p[2], p[0]))
        else:
            f.write(self.data)


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
        offset = 36 + self._sound.get_list_size()

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
            offset += self._palettes.get_size()
            f.write(struct.pack("<H", offset))  # Tileset offset
            offset += self._tiles.get_size()
            f.write(struct.pack("<H", offset))  # Tilemap offset
            offset += self._tilemap.get_size()
            f.write(struct.pack("<H", self._tilemap.get_horz_offset()))
            f.write(struct.pack("<H", self._tilemap.get_vert_offset()))
            f.write(struct.pack("B", self._tilemap.width))
            f.write(struct.pack("B", self._tilemap.height))
            f.write(struct.pack("<HH", offset, 0x600))
            offset += self._vblankcode.get_size()
            f.write(struct.pack("<BB", self._consoleName.horizontal.x,
                                       self._consoleName.horizontal.y))
            f.write(struct.pack("<BB", self._consoleName.vertical.x,
                                       self._consoleName.vertical.y))
            f.write(struct.pack("xx"))
            f.write(struct.pack("<H", offset))
            offset += self._sound.get_size()
            self._sound.write_list(f, offset)

            self._palettes.write(f)

            self._tiles.write(f)
            self._tilemap.write(f)
            self._vblankcode.write(f)
            self._sound.write(f)
            self._sound.write_ch(f)

            print("Output size: {t}".format(t=f.tell()))

            if f.tell() > 0x3DB:
                raise Exception("This boot splash is bigger than 987 bytes and will not work.")


def main():
    print("WonderSwan SplashBuilder - {ver}".format(ver=__version__))

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

    try:
        bs = BootSplash(config)
        bs.write(args.output)
    except FileNotFoundError as e:
        print("Error: The file '{f}' cannot be found,"
              " please check your config file".format(f=e.filename))
    except Exception as e:
        print("Error: {e}".format(e=e))

