# Scarface CSO Bytecode - Complete Opcode Reference
## Extracted from BrokenFace Decompiler

**Source:** BrokenFace codec.py lines 1461-1548  
**Date:** December 31, 2025  
**Total Opcodes:** 86 defined (0-85)

---

## Complete Opcode Mapping

```
Dec | Hex | Opcode Name               | Handler Function
----|-----|---------------------------|----------------------
0   | 00  | OP_FUNC_DECL              | opFuncDecl
1   | 01  | OP_CREATE_OBJECT          | opCreateObject
2   | 02  | (undefined)               | -
3   | 03  | (undefined)               | -
4   | 04  | OP_ADD_OBJECT             | opAddObject
5   | 05  | OP_END_OBJECT             | opEndObject
6   | 06  | OP_JMPIFFNOT              | opJmpiffnot
7   | 07  | OP_JMPIFNOT               | opJmpifnot
8   | 08  | OP_JMPIFF                 | opJmpiff
9   | 09  | OP_JMPIF                  | opJmpif
10  | 0A  | OP_JMPIFNOT_NP            | opJmpifnotNp
11  | 0B  | OP_JMPIF_NP               | opJmpifNp
12  | 0C  | OP_JMP                    | opJmp
13  | 0D  | OP_RETURN                 | opReturn
14  | 0E  | OP_CMPEQ                  | opCmpeq
15  | 0F  | OP_CMPLT                  | opCmplt
16  | 10  | OP_CMPLE                  | opCmple
17  | 11  | OP_CMPGR                  | opCmpgr
18  | 12  | OP_CMPGE                  | opCmpge
19  | 13  | OP_CMPNE                  | opCmpne
20  | 14  | OP_XOR                    | opXor
21  | 15  | OP_MOD                    | opMod
22  | 16  | OP_BITAND                 | opBitand
23  | 17  | OP_BITOR                  | opBitor
24  | 18  | OP_NOT                    | opNot
25  | 19  | OP_NOTF                   | opNotf
26  | 1A  | OP_ONESCOMPLEMENT         | opOnescomplement
27  | 1B  | OP_SHR                    | opShr
28  | 1C  | OP_SHL                    | opShl
29  | 1D  | OP_AND                    | opAnd
30  | 1E  | OP_OR                     | opOr
31  | 1F  | OP_ADD                    | opAdd
32  | 20  | OP_SUB                    | opSub
33  | 21  | OP_MUL                    | opMul
34  | 22  | OP_DIV                    | opDiv
35  | 23  | OP_NEG                    | opNeg
36  | 24  | OP_SETCURVAR              | opSetcurvar
37  | 25  | OP_SETCURVAR_CREATE       | opSetcurvar
38  | 26  | OP_SETCURVAR_ARRAY        | opSetcurvar
39  | 27  | OP_SETCURVAR_ARRAY_CREATE | opSetcurvar
40  | 28  | OP_SETCURVAR_ARRAY        | opSetcurvarArray
41  | 29  | OP_SETCURVAR_ARRAY_CREATE | opSetcurvarArray
42  | 2A  | (variant)                 | opSetcurvarArray
43  | 2B  | (variant)                 | opSetcurvarArray
44  | 2C  | OP_LOADVAR_UINT           | opLoadvarUint
45  | 2D  | OP_LOADVAR_FLT            | opLoadvarFlt
46  | 2E  | OP_LOADVAR_STR            | opLoadvarStr
47  | 2F  | OP_SAVEVAR_UINT           | opSavevarUint
48  | 30  | OP_SAVEVAR_FLT            | opSavevarFlt
49  | 31  | OP_SAVEVAR_STR            | opSavevarStr
50  | 32  | OP_SETCUROBJECT           | opSetcurobject
51  | 33  | OP_SETCUROBJECT_NEW       | opSetcurobjectNew
52  | 34  | OP_SETCURFIELD            | opSetcurfield
53  | 35  | OP_SETCURFIELD_ARRAY      | opSetcurfieldArray
54  | 36  | OP_LOADFIELD_UINT         | opLoadfieldUint
55  | 37  | OP_LOADFIELD_FLT          | opLoadfieldFlt
56  | 38  | OP_LOADFIELD_STR          | opLoadfieldStr
57  | 39  | OP_SAVEFIELD_UINT         | opSavefieldUint
58  | 3A  | OP_SAVEFIELD_FLT          | opSavefieldFlt
59  | 3B  | OP_SAVEFIELD_STR          | opSavefieldStr
60  | 3C  | OP_STR_TO_UINT            | opStrToUint
61  | 3D  | OP_STR_TO_FLT             | opStrToFlt
62  | 3E  | OP_STR_TO_NONE            | opStrToNone
63  | 3F  | OP_FLT_TO_UINT            | opFltToUint
64  | 40  | OP_FLT_TO_STR             | opFltToStr
65  | 41  | OP_FLT_TO_NONE            | opFltToNone
66  | 42  | OP_UINT_TO_FLT            | opUintToFlt
67  | 43  | OP_UINT_TO_STR            | opUintToStr
68  | 44  | OP_UINT_TO_NONE           | opUintToNone
69  | 45  | OP_LOADIMMED_UINT         | opLoadimmedUint
70  | 46  | OP_LOADIMMED_FLT          | opLoadimmedFlt
71  | 47  | OP_LOADIMMED_STR          | opLoadimmedStr
72  | 48  | OP_LOADIMMED_IDENT        | opLoadimmedIdent
73  | 49  | OP_TAG_TO_STR             | opTagToStr
74  | 4A  | OP_CALLFUNC               | opCallfunc
75  | 4B  | OP_CALLFUNC_RESOLVE       | opCallfunc
76  | 4C  | (undefined)               | -
77  | 4D  | OP_ADVANCE_STR            | opAdvanceStr
78  | 4E  | OP_ADVANCE_STR_APPENDCHAR | opAdvanceStrAppendchar
79  | 4F  | OP_ADVANCE_STR_COMMA      | opAdvanceStrComma
80  | 50  | OP_ADVANCE_STR_NUL        | opAdvanceStrNul
81  | 51  | OP_REWIND_STR             | opRewindStr
82  | 52  | OP_TERMINATE_REWIND_STR   | opTerminateRewindStr
83  | 53  | OP_COMPARE_STR            | opCompareStr
84  | 54  | OP_PUSH                   | opPush
85  | 55  | OP_PUSH_FRAME             | opPushFrame
```

---

## Critical Corrections

### My Previous Mapping (WRONG)

I had assumed the Torque3D opcode order, which was:
- OP_SAVEFIELD_STR = 0x55 (85)
- OP_SETCURFIELD = 0x48 (72)
- etc.

### Actual Scarface Mapping (CORRECT)

- 0x55 (85) = OP_PUSH_FRAME
- 0x48 (72) = OP_LOADIMMED_IDENT
- 0x52 (82) = OP_TERMINATE_REWIND_STR
- 0x54 (84) = OP_PUSH
- 0x4A (74) = OP_CALLFUNC
- 0x3E (62) = OP_STR_TO_NONE

---

## Re-Analysis: fecontrolobject.cso

With correct opcodes, let's re-decode the bytecode:

### Bytecode (hex)
```
55 48 00 0c 54 4a 00 00 00 00 00 3e
```

### Correct Decoding
```
Position | Hex  | Opcode               | Analysis
---------|------|----------------------|------------------------
0        | 55   | OP_PUSH_FRAME        | Start function call frame
1        | 48   | OP_LOADIMMED_IDENT   | Load identifier
2-3      | 00 0C| → offset 0x000C      | "Control Object"
4        | 54   | OP_PUSH              | Push to stack
5        | 4A   | OP_CALLFUNC          | Call function
6-10     | 00..00| → function params    | 
11       | 3E   | OP_STR_TO_NONE       | Clear string stack
```

This matches the decompiled:
```torquescript
stxldpahbdn("Control Object");
```

Where `stxldpahbdn` is a hashed function name at offset 0x0000!

---

## Opcode Parameter Patterns

### Pattern A: No Parameters (1 byte total)

```
Opcode | Name                | Parameters
-------|---------------------|------------
0x0D   | OP_RETURN           | None
0x18   | OP_NOT              | None
0x1F   | OP_ADD              | None
0x20   | OP_SUB              | None
0x3E   | OP_STR_TO_NONE      | None
0x54   | OP_PUSH             | None
0x55   | OP_PUSH_FRAME       | None
```

### Pattern B: 2-Byte Offset BIG-ENDIAN (3 bytes total)

```
Opcode | Name                | Format
-------|---------------------|---------------------
0x24   | OP_SETCURVAR        | opcode + offset(BE)
0x34   | OP_SETCURFIELD      | opcode + offset(BE)
0x47   | OP_LOADIMMED_STR    | opcode + offset(BE)
0x48   | OP_LOADIMMED_IDENT  | opcode + offset(BE)
```

### Pattern C: 1-Byte Value (2 bytes total)

```
Opcode | Name                | Format
-------|---------------------|---------------------
0x0C   | OP_JMP              | opcode + target(U8)
0x45   | OP_LOADIMMED_UINT   | opcode + value(U8)
0x4E   | OP_ADVANCE_STR_..   | opcode + char(U8)
```

### Pattern D: Complex Multi-Byte

```
Opcode | Name                | Format
-------|---------------------|---------------------
0x00   | OP_FUNC_DECL        | See detailed format below
0x01   | OP_CREATE_OBJECT    | See detailed format below
0x4A   | OP_CALLFUNC         | See detailed format below
```

---

## OP_FUNC_DECL Format (0x00)

```
Byte | Type    | Description
-----|---------|--------------------------------
0    | U8      | Opcode (0x00)
1-2  | U16 BE  | Function name offset
3-4  | U16 BE  | Namespace offset (0 = none)
5-6  | U16 BE  | Package offset (0 = none)
7    | U8      | Has body (1 = yes, 0 = no)
8    | U8      | End code index
9    | U8      | Argument count (argc)
10+  | U16 BE  | Arg offsets (2 bytes each × argc)
```

**Total size:** 10 + (argc × 2) bytes

---

## OP_CALLFUNC Format (0x4A)

```
Byte | Type    | Description
-----|---------|--------------------------------
0    | U8      | Opcode (0x4A)
1-2  | U16 BE  | Function name offset
3-4  | U16 BE  | Namespace offset
5    | U8      | Call type (0=func, 1=method)
```

**Total size:** 6 bytes

---

## String Push Pattern

Common pattern for pushing string arguments:

```
55        | OP_PUSH_FRAME
48 XX XX  | OP_LOADIMMED_IDENT offset
54        | OP_PUSH
4A ...    | OP_CALLFUNC
3E        | OP_STR_TO_NONE (cleanup)
```

---

## Summary

### Key Corrections Made

1. ✅ Opcodes 0-85 mapped correctly from BrokenFace
2. ✅ OP_PUSH_FRAME = 0x55 (not OP_SAVEFIELD_STR)
3. ✅ OP_LOADIMMED_IDENT = 0x48 (not OP_SETCURFIELD)
4. ✅ OP_PUSH = 0x54 (not OP_SAVEFIELD_UINT)
5. ✅ OP_CALLFUNC = 0x4A (not OP_LOADFIELD_UINT)

### What This Means

All previous bytecode analysis was using WRONG opcode numbers!

The compiler must use the CORRECT Scarface opcode values, not Torque3D's values.

---

**File Size:** ~8 KB

**Status:** Opcode mapping corrected, ready for accurate bytecode analysis
