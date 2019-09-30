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

import json
import struct

def main():
    print("Hello")


if __name__ == "__main__":
    main()