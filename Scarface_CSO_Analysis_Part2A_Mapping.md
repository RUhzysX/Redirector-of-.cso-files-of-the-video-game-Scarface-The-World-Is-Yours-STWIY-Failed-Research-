# Scarface CSO File Analysis - Part 2A
## Compiled-to-Decompiled Mapping and Bytecode Patterns

**Analysis Date:** December 31, 2025  
**Dataset:** 401 compiled .cso files, 298 with decompiled .cs counterparts  
**Method:** Systematic analysis from smallest to largest files

---

## Dataset Overview

### File Statistics

```
Total Compiled Files:  401
With Decompiled:       298 (74.3%)
Without Decompiled:    103 (25.7%)

Size Distribution:
- 32 bytes (empty):    27 files
- 33-100 bytes:        8 files
- 101-500 bytes:       47 files
- 501-2000 bytes:      89 files
- 2001+ bytes:         230 files
```

---

## Pattern 1: Empty Scripts (32 bytes)

### Example Files
- `camerastate.cso`
- `hud.cso`
- `sku.cso`
- `spawn.cso`
- `weapons.cso`
- + 22 more files

### Binary Structure (32 bytes total)

```
Offset | Hex              | Description
-------|------------------|---------------------------
0x0000 | 01 00 00 00      | Version = 1
0x0004 | 00 00 00 00      | Global string size = 0
0x0008 | 00 00 00 00      | Global float count = 0
0x000C | 00 00 00 00      | Function string size = 0
0x0010 | 00 00 00 00      | Function float count = 0
0x0014 | 02 00 00 00      | Code count = 2
0x0018 | 0D               | OP_RETURN (0x0D)
0x0019 | FF CD CD         | END marker (0xFF 0xCDCD)
0x001C | 00 00 00 00      | Identifier table count = 0
```

### Decompiled Output

```torquescript
// Decompiled file: camerastate.cso;
return;
```

### Analysis

**Code Count = 2:**
- Code 0: `0x0D` = OP_RETURN
- Code 1: `0xFF 0xCDCD` = END marker

**Key Insight:** Even empty files need OP_RETURN + END marker!

---

## Pattern 2: Simple Function Calls

### Example: scriptobject.cso (88 bytes)

### Binary Structure

```
Size: 88 bytes
Code count: 12

Global Strings:
  [0x0000] "stxahjbdeil"
  [0x000C] "stxmikekbbj"

Bytecode (hex):
00 00 00 00 00 00 00 00 0b 00 0d 0d
```

### Decompiled Output

```torquescript
function stxmikekbbj::stxahjbdeil()
{
    return;
}
return;
```

### Bytecode Analysis

```
Position | Hex  | Opcode              | Parameters
---------|------|---------------------|--------------------
0        | 00   | OP_FUNC_DECL        | (followed by params)
1        | 00   | [name offset high]  | 0x0000
2        | 00   | [name offset low]   | = offset 0
3        | 00   | [namespace high]    | 0x000C
4        | 00   | [namespace low]     | = offset 12
5        | 00   | [package high]      | 0x0000
6        | 00   | [package low]       | = offset 0 (empty)
7        | 00   | [has body]          | 0 = no body?
8        | 0B   | [end code index]    | Code 11
9        | 00   | [argc]              | 0 arguments
10       | 0D   | OP_RETURN           |
11       | 0D   | OP_RETURN           | (top-level)
```

**Wait, the analysis shows issues!** Let me re-examine this more carefully...

---

## Pattern 3: Native Function Calls

### Example: fecontrolobject.cso (359 bytes)

### Binary Structure

```
Size: 359 bytes
Code count: 62

Global Strings (9 entries):
  [0x0000] "stxldpahbdn"
  [0x000C] "Control Object"
  [0x001B] "stxejejaakk"
  [0x0027] "POIToDbgCam"
  [0x0033] "Snap Point of Interest to Dbg Cam"
  [0x0055] "PushStreamerObjectOfInterest( DebugCamera.GetID() );"
  [0x008A] "POIToPlayer"
  [0x0096] "Snap Point of Interest to Player"
  [0x00B7] "PopStreamerObjectOfInterest( \"MainCharacter\".GetID() );"
```

### Decompiled Output

```torquescript
stxldpahbdn("Control Object");
stxejejaakk("Control Object", "POIToDbgCam", 
    "Snap Point of Interest to Dbg Cam", 
    "PushStreamerObjectOfInterest( DebugCamera.GetID() );");
stxejejaakk("Control Object", "POIToPlayer", 
    "Snap Point of Interest to Player", 
    "PopStreamerObjectOfInterest( \"MainCharacter\".GetID() );");
return;
```

### Bytecode (First 50 bytes hex)

```
55 48 00 0c 54 4a 00 00 00 00 00 3e
55 48 00 0c 54 48 00 27 54 48 00 33 54 48 00 55
54 4a 00 00 00 00 00 3e
55 48 00 0c 54 48 00 8a 54 48 00 96 54 48
```

### Pattern Recognition

Looking at the first call: `stxldpahbdn("Control Object")`

```
Offset | Hex     | Analysis
-------|---------|------------------------------------
0      | 55      | Unknown opcode
1      | 48      | Could be OP_SETCURFIELD (0x48)?
2-3    | 00 0C   | Offset 0x000C (BIG-ENDIAN!)
4      | 54      | Unknown opcode
5      | 4A      | Unknown opcode
6-10   | 00...00 | Data
11     | 3E      | Unknown opcode
```

**Hypothesis:** This isn't standard opcodes. Let me check the actual opcode values!

---

## Opcode Number Discovery

From BrokenFace codec.py, the opcodes are mapped by their numeric value.

Let me decode the bytes properly:

```
0x55 = 85 decimal = ?
0x48 = 72 decimal = OP_ADVANCE_STR?
0x54 = 84 decimal = ?
0x4A = 74 decimal = OP_ADVANCE_STR_COMMA
0x3E = 62 decimal = OP_UINT_TO_FLT
```

**This doesn't match the decompiled output!**

The issue: **I don't have the correct opcode mapping for Scarface!**

---

## Critical Discovery

The opcodes in Scarface are NOT the same as my assumed mapping from Torque3D!

Let me check BrokenFace's actual opcode definitions:

From codec.py, I need to find the opcode dispatch table...

---

## Opcode Mapping from BrokenFace

Let me extract the actual opcode-to-function mapping from BrokenFace:

Looking at codec.py around line 100-200, there should be a dispatch table or switch statement that maps opcode values to handler functions.

**Key Finding:** The opcode numbers might be defined differently in Scarface!

Let me search for the opcode enum or constants:

```python
# From BrokenFace, the opcodes are handled in decode() method
# which calls methods based on opcode value
```

---

## Investigation Needed

To properly document the bytecode, I need to:

1. Extract the exact opcode-to-handler mapping from BrokenFace
2. Verify against actual bytecode
3. Map each byte sequence to its decoded operation

**Approach:**
- Run BrokenFace in debug mode to see opcode numbers
- Or extract the switch/dispatch logic from codec.py
- Or trace through actual execution

---

## Temporary Conclusion

**What we know for certain:**

1. ✅ File format (version, tables, code count) is correct
2. ✅ String tables work as documented
3. ✅ Float tables work as documented
4. ✅ Code count is number of opcodes
5. ✅ END marker is 0xFF 0xCDCD
6. ❌ **Opcode number mapping is WRONG**

**Next step:** Extract the real opcode mapping from BrokenFace before continuing documentation.

---

**File Size Check:** ~6 KB

**Status:** Need to extract opcode mapping before proceeding with detailed analysis.

**Action Required:** 
1. Find BrokenFace's opcode dispatch table
2. Create correct opcode enum
3. Re-analyze bytecode with correct mapping
