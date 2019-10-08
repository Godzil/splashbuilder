WonderSwan SplashBuilder
========================

This tool is made to help you build custom boot splash for the Bandai WonderSwan Color and SwanCrystal.


# **Warning**:
Installing a custom bootsplash on your own console __is at your own risk__. It is really easy to brick your
console if something is wrong, and there is only one way to recover from that which is to have a special cartridge that
forbid the user bootsplash to run (look further in the document on what are the requirement for that).

**ALWAYS EXTENSIVELY TEST WITH AN EMULATOR BEFORE EVEN TRYING ON A REAL CONSOLE.**


There is also currently (as of 2019-09-08) no tool to install a custom bootsplash in your WonderSwan EEPROM.
I will eventually provide such a tool at a later point.


#### Installing SplashBuilder

You first need to install this tool. You can either use directly from the github sources, or (recommended) install
using pip:

```
pip install splashbuilder
```

SplashBuilder is build using Python3 and some Linux distribution may force you to use `pip3` instead of `pip` to
install using Python 3.

You also need [https://www.nasm.us/](`nasm`) to be installed if you want to have your own code running in your bootsplash as a boot splash
include some code.

#### How to make a bootsplash

TO BE FINISHED




#### Some technical info about the boot splashes

The basis of the bootsplash is a structure containing certains fields:
```C
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
   uint8_t consoleNameHorizontalPosX;
   uint8_t consoleNameHorizontalPosY;
   uint8_t consoleNameVerticalPosX;
   uint8_t consoleNameVerticalPosY;
   uint8_t padding3[2];
   uint16_t soundSampleOffset;
   uint16_t soundChannelDataOffset[]
};
```

that you will find in the internal EEPROM starting from 80h in 8bit mode or 40h in 16bit access mode (that how the
WonderSwan is accessing the EEPROM)

Here are a description of the fields

* `consoleFlags`: This byte store some information about the console configuration:
    * `bit 7`: 1 = Custom boot splash enabled
    * `bit 6`: 1 = High contrast mode (WonderSwan Color only)
    * `bit 5-2`: Ignored
    * `bit 1-0`: Default volume level
* `consoleNameColor`: This byte set the default color used by the sprites for the console name.
Only value from 0 to 15 are valid. Here is the list of available colors (order is left to right, top to bottom)

![ConsoleNameColors](doc/ConsoleNameColors.png)
* `size`: The size of the bootsplash. Only two valid values: 0 a 1. 0 mean the size is up to 1BDh, 1 mean the size
is up to 3BDh. You can safely leave that value to 1.
* `startFrame` and `endFrame`: The code in the bootrom count the number of frames from 0 to 255. Both value tell it
when your splash need to be displayed, and when it end. When it reach the end, the game is going to be booted.
* `spriteCount`: The number of sprite your bootsplash use.
* `paletteFlags`:
    * `bit 7`: Bootsplash BPP mode. 0 = 1BPP, 1 = planar 2BPP
    * `bit 6-5`: ignored
    * `bit 4-0`: number of palettes defined in the bootsplash. For some bizarre reason, the bootrom allow values up to
    32 which make no sense knowing that the hardware support only up to 16 palettes.
* `tilesCount`: The number of tiles your bootsplash provide.
* `paletteOffset`, `tilesetOffset`, `tilemapOffset`: offset in the bootsplash file where the palette, tileset and
default tilemap will be found.
* `horizontalTilemapDestOffset`: The offset (as in address) in SCREEN1 where the tilemap has to be copied when the
console start in horizontal mode.
* `verticalTilemapDestOffset`: The offset (as in address) in SCREEN1 where the tilemap has to be copied when the
console start in vertical mode.
* `tilemapWidth`: the width of your default tilemap
* `tilemapHeight: the height of your default tilemap`
* `splashCodePointer`: The far pointer to the code you include in the bootsplash. **Warning** it is a `far` pointer, so
both offset and segment need to be given, but the segment is fixed and need to be 0600h. Your code also need to be valid
and return with a `retf` (CBh) instruction and not a `ret` (C3h).
* `consoleNameHorizontalPosX`, `consoleNameHorizontalPosY`: The position in pixel in horizontal mode of the console name
* `consoleNameVerticalPosX`, `consoleNameVerticalPosY`: The position in pixel in vertical mode of the console name
* `soundSampleOffset`: The offset in the bootsplash file where the 4 waveform are set for each audio channel
* `soundChannelDataOffset[]` This is a list of offset for the data used to play notes on each audio channel. This list
need to be ended with FFFFh after the last offset is given. so for 2 channel used, you will get
```
XXXXh, YYYYh, FFFFh
```

Then it is followed by each block that are listed by the header:
- Palette
- Tileset
- Tilemap
- Audio waveforms
- Audio data for each channel used
- VBlank code

##### IRAM Memory map used by the boot rom for the bootsplash:

```
0000h - 07FFh: internal data for the bootrom. >> Don't touch it
0800h - 0FFFh: Tilemap for Screen 1
1000h - 17FFh: Tilemap for Screen 2
1800h - 1FFFh: Sprite list
2000h - 3FFFh: 2BPP Tileset
4000h - 5FFFh: N/A
6000h - 6FFFh: Boot splash data >> Don't touch it
7000h - 7FFFh: Bootsplash data
8000h - FDFFh: N/A
FE00h - FFFFh: Palette data
```

The bootsplash data region contain by default some informations which is better to not touch:

`7000h`: store the screen orientation

##### Tileset BPP
It may sounds weird, but the bootsplah support one well know mode, the planar 2bpp, but also a 1bpp mode which in theory
the console does not support. For that the bootroom will automatically convert it to the planar 2bpp mode. This mode
allow to save space if you don't need 4 colors per tiles.

The palette definition will also change depending on the BPP set. You only need to provide two colors per palette in
1BPP mode, and four in 2BPP mode.

##### How the segment register in the vblank code
```
CS = 0600h
DS = 0600h
ES = ??
SS = 0000h
```
__DO NOT CHANGE THEM UNLESS YOU ARE SURE TO RESTORE THEM__

##### Sounds data channel format
Each "note" are defined by a 32bit value:
```
DDVVPPPP:
DD   = duration (8 bit) (in vblank frame)
VV   = Volume (8bit)
PPPP = Pitch (16bit)
```
If pitch bit 7 is set then the channel is stopped.


#### How to recover a bricked WonderSwan
**Q:** HELP, I made booboo and tried my bootsplash on real hardware and bricked my Wonderswan.

**A:** Well it is not like if I haven't put a warning at the beginning of this file.

There is two way to recover from that. And both are not easy.

The first method is to use some external hardware to write to the internal EEPROM and change the consoleFlag byte to
disable the Custom boot splash. Easy some would say, but you need to open your console, connect some wire
(but probably you will need to desolder the chip) and use some tool to write to the EEPROM. Not something that everyone
can do.

The second method, which will be easier in the end, but there is currently no such tool available, a cartridge can force
the bootrom to ignore a custom boot splash. Bandai/Koto was wise enough to add that, but there is no commercial games
(including the WonderWitch) which are configured to do that.
There is also at the moment of writing no Flash cart that allow that.
The bit that need to be set to 1 is part of the cartridge metadata.
In the last 16 bytes you will find the reset vector and some information about the game:
```
00h - 04h: JMP FAR instruction for the reset vector
05h      : ???
06h      : Publisher ID
07h - 08h: Game IO
09h      : Game revision
0Ah      : ROM size
0Bh      : Save type / size
0Ch - 0Dh: Cart flags
0Eh - 0Fh: ROM CRC
```

The byte 5 is a bit of a weird byte here:
- `bit 7`: Set = ignore custom bootsplash
- `bit 6-4`: ignored
- `bit 3-0`: if set the console refuse to boot. Why? (I suspect this is related with Devkit cartridges)

_To WonderSwan flash cart manufacturer_: I highly recommend that your flash cart have the possibility to set the bit 7
of byte 5 to 1, either permanently, or in any way that does not involve using a console, so people could recover from a
badly installed bootsplash.
