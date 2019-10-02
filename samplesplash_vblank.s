
vblank:
    pusha
    add word [SS:0xFE00], 0x111
    mov AL, byte [SS:0x7002]
    out 0x15, AL
    inc byte [SS:0x7001]
    inc byte [SS:0x7002]
    POPA
    RETF