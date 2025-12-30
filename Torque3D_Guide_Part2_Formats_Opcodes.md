# Torque3D Engine Analysis & Scarface Compiler Guide - Part 2
### File Formats & Opcode Comparison

**Continued from Part 1**

---

## 4. DSO File Format Specification

### 4.1 Torque3D DSO Format (Standard)

```
┌────────────────────────────────────────────────────────────────┐
│              Torque3D .dso File Binary Structure                │
└────────────────────────────────────────────────────────────────┘

Offset  │ Size    │ Field                       │ Type    │ Notes
────────┼─────────┼─────────────────────────────┼─────────┼──────────────
0x0000  │ 4       │ DSO Version                 │ U32     │ Con::DSOVersion
0x0004  │ 4       │ Global String Table Size    │ U32     │ Byte size
0x0008  │ varies  │ Global String Table Data    │ char[]  │ Null-terminated strings
        │ 4       │ Global Float Table Size     │ U32     │ Byte size (count * 8)
        │ varies  │ Global Float Table Data     │ F64[]   │ 8 bytes each
        │ 4       │ Function String Table Size  │ U32     │ Byte size
        │ varies  │ Function String Table Data  │ char[]  │ Null-terminated strings
        │ 4       │ Function Float Table Size   │ U32     │ Byte size (count * 8)
        │ varies  │ Function Float Table Data   │ F64[]   │ 8 bytes each
        │ 4       │ Code Size                   │ U32     │ Number of U32 instructions
        │ 4       │ Line Break Pair Count       │ U32     │ Debug info count
        │ varies  │ Bytecode (compressed)       │ U8/U32  │ See compression below
        │ varies  │ Line Break Pairs            │ U32[]   │ [line, ip] pairs
        │ 4       │ Identifier Count            │ U32     │ Number of identifiers
        │ varies  │ Identifier Table            │ varies  │ See format below
```

### 4.2 Scarface CSO Format (Modified)

```
┌────────────────────────────────────────────────────────────────┐
│              Scarface .cso File Binary Structure                │
└────────────────────────────────────────────────────────────────┘

Offset  │ Size    │ Field                       │ Type    │ Notes
────────┼─────────┼─────────────────────────────┼─────────┼──────────────
0x0000  │ 4       │ Script Version              │ U32     │ Always 1
0x0004  │ 4       │ Global String Table Size    │ U32     │ Byte size
0x0008  │ varies  │ Global String Table Data    │ char[]  │ Null-terminated strings
        │ 4       │ Global Float Table Count    │ U32     │ COUNT not bytes! ⚠️
        │ varies  │ Global Float Table Data     │ F32[]   │ 4 bytes each ⚠️
        │ 4       │ Function String Table Size  │ U32     │ Byte size
        │ varies  │ Function String Table Data  │ char[]  │ Null-terminated strings
        │ 4       │ Function Float Table Count  │ U32     │ COUNT not bytes! ⚠️
        │ varies  │ Function Float Table Data   │ F32[]   │ 4 bytes each ⚠️
        │ 4       │ Bytecode Size               │ U32     │ Number of codes
        │ varies  │ Bytecode                    │ varies  │ Special encoding
        │ 4       │ Identifier Count            │ U32     │ Number of identifiers
        │ varies  │ Identifier Table            │ varies  │ Patching info
        │         │ [NO LINE BREAK DATA]        │         │ Not present! ⚠️
```

### 4.3 Critical Format Differences

| Aspect | Torque3D | Scarface | Impact |
|--------|----------|----------|--------|
| **Version** | Variable (DSO version) | Always 1 | Low |
| **Float Type** | F64 (8 bytes) | F32 (4 bytes) | **CRITICAL** |
| **Float Size Field** | Byte size (count × 8) | Entry count | **HIGH** |
| **Line Breaks** | Included after bytecode | Not present | **HIGH** |
| **Bytecode Encoding** | 0xFF marker + U32 | Different encoding | **MODERATE** |
| **Debug Info** | Full support | None | Low |

### 4.4 Bytecode Compression Details

**Torque3D Compression:**
```cpp
// Writing
for (U32 i = 0; i < codeSize; i++) {
    if (code[i] < 0xFF) {
        st.write(U8(code[i]));              // 1 byte
    } else {
        st.write(U8(0xFF));                 // Marker
        st.write(code[i]);                  // 4 bytes
    }
}

// Reading
for (U32 i = 0; i < codeSize; i++) {
    U8 b;
    st.read(&b);
    if (b == 0xFF) {
        st.read(&code[i]);                  // Read full U32
    } else {
        code[i] = b;                        // Use byte value
    }
}
```

**Logic:** Values 0-254 stored as single byte, values ≥255 use 5 bytes (0xFF + 4-byte value)

**Scarface Encoding (from BrokenFace analysis):**
- 1-byte codes: 0x00-0xFE (normal opcodes)
- 2-byte codes: 0xFF + single byte (values 255-510)
- Multi-byte codes: Extended format for larger values

### 4.5 Identifier Table Format

```
┌──────────────────────────────────────┐
│      Identifier Table Entry          │
└──────────────────────────────────────┘

Offset  │ Size  │ Field
────────┼───────┼────────────────────────
0x00    │ 4     │ String Offset (in global string table)
0x04    │ 4     │ Usage Count (how many times this ident appears)
0x08    │ 4×N   │ Instruction Pointers (where to patch)
```

**Example:**
```
Identifier "playerHealth" appears 3 times:
  Offset: 42 (in global string table)
  Count: 3
  IPs: [120, 245, 389]
  
At runtime, these IPs get patched with StringTable entry pointer.
```

### 4.6 Binary Example - Simple Script

**Source (test.cs):**
```torquescript
function add(%a, %b) {
    return %a + %b;
}
```

**Compiled Hex Dump (Scarface format):**
```
00000000: 01 00 00 00              | Version: 1
00000004: 0A 00 00 00              | Global string size: 10 bytes
00000008: 61 64 64 00 61 00 62 00  | "add\0a\0b\0" (strings)
          
00000010: 00 00 00 00              | Global float count: 0
00000014: 00 00 00 00              | Function string size: 0
00000018: 00 00 00 00              | Function float count: 0
          
0000001C: 08 00 00 00              | Code size: 8 instructions
          
00000020: 00                       | OP_FUNC_DECL (0)
00000021: FF 00 00                 | [function metadata]
00000024: 28                       | OP_LOADVAR_FLT (40)
00000025: 29                       | OP_LOADVAR_FLT (41) 
00000026: 1F                       | OP_ADD (31)
00000027: 0D                       | OP_RETURN (13)
          
00000028: 02 00 00 00              | Ident count: 2
0000002C: ...                      | [ident table entries]
```

---

## 5. Opcode Comparison: Torque3D vs Scarface

### 5.1 Complete Opcode Mapping Table

| Dec | T3D Opcode | Scarface Opcode | Compatible? | Notes |
|-----|------------|-----------------|-------------|-------|
| 0 | OP_FUNC_DECL | OP_FUNC_DECL | ✅ YES | Function declaration |
| 1 | OP_CREATE_OBJECT | OP_CREATE_OBJECT | ✅ YES | Create new object |
| 2 | OP_ADD_OBJECT | OP_2 | ⚠️ DIFFERENT | T3D: add to parent; Scarface: continue marker |
| 3 | OP_END_OBJECT | OP_3 | ⚠️ DIFFERENT | T3D: end object; Scarface: continue marker |
| 4 | OP_FINISH_OBJECT | OP_ADD_OBJECT | ⚠️ RENUMBERED | Scarface uses old numbering |
| 5 | - | OP_END_OBJECT | - | Scarface #5 |
| 6 | OP_JMPIFFNOT | OP_JMPIFFNOT | ✅ YES | Jump if false (float) |
| 7 | OP_JMPIFNOT | OP_JMPIFNOT | ✅ YES | Jump if not |
| 8 | OP_JMPIFF | OP_JMPIFF | ✅ YES | Jump if false |
| 9 | OP_JMPIF | OP_JMPIF | ✅ YES | Jump if true |
| 10 | OP_JMPIFNOT_NP | OP_JMPIFNOT_NP | ✅ YES | Jump if not (no pop) |
| 11 | OP_JMPIF_NP | OP_JMPIF_NP | ✅ YES | Jump if (no pop) |
| 12 | OP_JMP | OP_JMP | ✅ YES | Unconditional jump |
| 13 | OP_RETURN | OP_RETURN | ✅ YES | Return from function |
| 14 | OP_RETURN_VOID | - | ❌ NO | Torque3D only |
| 15 | OP_RETURN_FLT | - | ❌ NO | Torque3D only |
| 16 | OP_RETURN_UINT | - | ❌ NO | Torque3D only |
| 17 | OP_CMPEQ | OP_CMPEQ (14) | ✅ YES | Compare equal |
| 18 | OP_CMPGR | OP_CMPLT (15) | ⚠️ SWAPPED! | Order differs |
| 19 | OP_CMPGE | OP_CMPLE (16) | ⚠️ SWAPPED! | Order differs |
| 20 | OP_CMPLT | OP_CMPGR (17) | ⚠️ SWAPPED! | Order differs |
| 21 | OP_CMPLE | OP_CMPGE (18) | ⚠️ SWAPPED! | Order differs |
| 22 | OP_CMPNE | OP_CMPNE (19) | ✅ YES | Compare not equal |
| 23 | OP_XOR | OP_XOR (20) | ✅ YES | Bitwise XOR |
| 24 | OP_MOD | OP_MOD (21) | ✅ YES | Modulo |
| 25 | OP_BITAND | OP_BITAND (22) | ✅ YES | Bitwise AND |
| 26 | OP_BITOR | OP_BITOR (23) | ✅ YES | Bitwise OR |
| 27 | OP_NOT | OP_NOT (24) | ✅ YES | Logical NOT |
| 28 | OP_NOTF | OP_NOTF (25) | ✅ YES | Logical NOT (float) |
| 29 | OP_ONESCOMPLEMENT | OP_ONESCOMPLEMENT (26) | ✅ YES | Bitwise NOT |
| 30 | OP_SHR | OP_SHR (27) | ✅ YES | Shift right |
| 31 | OP_SHL | OP_SHL (28) | ✅ YES | Shift left |
| 32 | OP_AND | OP_AND (29) | ✅ YES | Logical AND |
| 33 | OP_OR | OP_OR (30) | ✅ YES | Logical OR |
| 34 | OP_ADD | OP_ADD (31) | ✅ YES | Addition |
| 35 | OP_SUB | OP_SUB (32) | ✅ YES | Subtraction |
| 36 | OP_MUL | OP_MUL (33) | ✅ YES | Multiplication |
| 37 | OP_DIV | OP_DIV (34) | ✅ YES | Division |
| 38 | OP_NEG | OP_NEG (35) | ✅ YES | Negation |
| 39 | OP_INC | - | ❌ NO | Torque3D only |
| 40 | OP_DEC | - | ❌ NO | Torque3D only |
| 41 | OP_SETCURVAR | OP_SETCURVAR (36) | ✅ YES | Set current variable |
| 42 | OP_SETCURVAR_CREATE | OP_SETCURVAR_CREATE (37) | ✅ YES | Create & set var |
| 43 | OP_SETCURVAR_ARRAY | OP_SETCURVAR_ARRAY (38) | ✅ YES | Set array var |
| 44 | OP_SETCURVAR_ARRAY_VARLOOKUP | - | ❌ NO | Torque3D only |
| 45 | OP_SETCURVAR_ARRAY_CREATE | OP_SETCURVAR_ARRAY_CREATE (39) | ✅ YES | Create array var |
| 46 | OP_SETCURVAR_ARRAY_CREATE_VARLOOKUP | - | ❌ NO | Torque3D only |
| 47 | OP_LOADVAR_UINT | OP_LOADVAR_UINT (40) | ✅ YES | Load uint from var |
| 48 | OP_LOADVAR_FLT | OP_LOADVAR_FLT (41) | ✅ YES | Load float from var |
| 49 | OP_LOADVAR_STR | OP_LOADVAR_STR (42) | ✅ YES | Load string from var |
| 50 | OP_LOADVAR_VAR | - | ❌ NO | Torque3D only |
| 51 | OP_SAVEVAR_UINT | OP_SAVEVAR_UINT (43) | ✅ YES | Save uint to var |
| 52 | OP_SAVEVAR_FLT | OP_SAVEVAR_FLT (44) | ✅ YES | Save float to var |
| 53 | OP_SAVEVAR_STR | OP_SAVEVAR_STR (45) | ✅ YES | Save string to var |
| 54 | OP_SAVEVAR_VAR | - | ❌ NO | Torque3D only |
| 55 | OP_SETCUROBJECT | OP_SETCUROBJECT (46) | ✅ YES | Set current object |
| 56 | OP_SETCUROBJECT_NEW | OP_SETCUROBJECT_NEW (47) | ✅ YES | Create new object |
| 57 | OP_SETCUROBJECT_INTERNAL | - | ❌ NO | Torque3D only |
| 58 | OP_SETCURFIELD | OP_SETCURFIELD (48) | ✅ YES | Set field name |
| 59 | OP_SETCURFIELD_ARRAY | OP_SETCURFIELD_ARRAY (49) | ✅ YES | Set field array |
| 60 | OP_SETCURFIELD_TYPE | - | ❌ NO | Torque3D only |
| 61 | OP_SETCURFIELD_ARRAY_VAR | - | ❌ NO | Torque3D only |
| 62 | OP_SETCURFIELD_THIS | - | ❌ NO | Torque3D only |
| 63 | OP_LOADFIELD_UINT | OP_LOADFIELD_UINT (50) | ✅ YES | Load uint field |
| 64 | OP_LOADFIELD_FLT | OP_LOADFIELD_FLT (51) | ✅ YES | Load float field |
| 65 | OP_LOADFIELD_STR | OP_LOADFIELD_STR (52) | ✅ YES | Load string field |
| 66 | OP_SAVEFIELD_UINT | OP_SAVEFIELD_UINT (53) | ✅ YES | Save uint field |
| 67 | OP_SAVEFIELD_FLT | OP_SAVEFIELD_FLT (54) | ✅ YES | Save float field |
| 68 | OP_SAVEFIELD_STR | OP_SAVEFIELD_STR (55) | ✅ YES | Save string field |
| 69 | OP_STR_TO_UINT | OP_STR_TO_UINT (56) | ✅ YES | Convert string→uint |
| 70 | OP_STR_TO_FLT | OP_STR_TO_FLT (57) | ✅ YES | Convert string→float |
| 71 | OP_STR_TO_NONE | OP_STR_TO_NONE (58) | ✅ YES | Convert string→none |
| 72 | OP_FLT_TO_UINT | OP_FLT_TO_UINT (59) | ✅ YES | Convert float→uint |
| 73 | OP_FLT_TO_STR | OP_FLT_TO_STR (60) | ✅ YES | Convert float→string |
| 74 | OP_FLT_TO_NONE | OP_FLT_TO_NONE (61) | ✅ YES | Convert float→none |
| 75 | OP_UINT_TO_FLT | OP_UINT_TO_FLT (62) | ✅ YES | Convert uint→float |
| 76 | OP_UINT_TO_STR | OP_UINT_TO_STR (63) | ✅ YES | Convert uint→string |
| 77 | OP_UINT_TO_NONE | OP_UINT_TO_NONE (64) | ✅ YES | Convert uint→none |
| 78 | OP_COPYVAR_TO_NONE | - | ❌ NO | Torque3D only |
| 79 | OP_LOADIMMED_UINT | OP_LOADIMMED_UINT (65) | ✅ YES | Load immediate uint |
| 80 | OP_LOADIMMED_FLT | OP_LOADIMMED_FLT (66) | ✅ YES | Load immediate float |
| 81 | OP_TAG_TO_STR | OP_TAG_TO_STR (67) | ✅ YES | Tag to string |
| 82 | OP_LOADIMMED_STR | OP_LOADIMMED_STR (68) | ✅ YES | Load immediate string |
| 83 | OP_DOCBLOCK_STR | - | ❌ NO | Torque3D only |
| 84 | OP_LOADIMMED_IDENT | OP_LOADIMMED_IDENT (69) | ✅ YES | Load identifier |
| 85 | OP_CALLFUNC_RESOLVE | OP_CALLFUNC_RESOLVE (70) | ✅ YES | Resolve function |
| 86 | OP_CALLFUNC | OP_CALLFUNC (71) | ✅ YES | Call function |
| 87 | OP_CALLFUNC_POINTER | - | ❌ NO | Torque3D only |
| 88 | OP_CALLFUNC_THIS | - | ❌ NO | Torque3D only |
| 89 | OP_ADVANCE_STR | OP_ADVANCE_STR (72) | ✅ YES | Advance string ptr |
| 90 | OP_ADVANCE_STR_APPENDCHAR | OP_ADVANCE_STR_APPENDCHAR (73) | ✅ YES | Append character |
| 91 | OP_ADVANCE_STR_COMMA | OP_ADVANCE_STR_COMMA (74) | ✅ YES | Add comma |
| 92 | OP_ADVANCE_STR_NUL | OP_ADVANCE_STR_NUL (75) | ✅ YES | Add null term |
| 93 | OP_REWIND_STR | OP_REWIND_STR (76) | ✅ YES | Rewind string |
| 94 | OP_TERMINATE_REWIND_STR | OP_TERMINATE_REWIND_STR (77) | ✅ YES | Terminate & rewind |
| 95 | OP_COMPARE_STR | OP_COMPARE_STR (78) | ✅ YES | Compare strings |
| 96 | OP_PUSH | OP_PUSH (79) | ✅ YES | Push string arg |
| 97 | OP_PUSH_UINT | - | ❌ NO | Use OP_PUSH instead |
| 98 | OP_PUSH_FLT | - | ❌ NO | Use OP_PUSH instead |
| 99 | OP_PUSH_VAR | - | ❌ NO | Use OP_PUSH instead |
| 100 | OP_PUSH_THIS | - | ❌ NO | Torque3D only |
| 101 | OP_PUSH_FRAME | OP_PUSH_FRAME (80) | ✅ YES | Push call frame |
| 102 | OP_ASSERT | - | ❌ NO | Torque3D only |
| 103 | OP_BREAK | - | ❌ NO | Torque3D only |
| 104 | OP_ITER_BEGIN | - | ❌ NO | Torque3D only |
| 105 | OP_ITER_BEGIN_STR | - | ❌ NO | Torque3D only |
| 106 | OP_ITER | - | ❌ NO | Torque3D only |
| 107 | OP_ITER_END | - | ❌ NO | Torque3D only |
| 108 | OP_INVALID | - | ❌ NO | Torque3D only |

### 5.2 Compatibility Summary

**✅ Directly Compatible: 69 opcodes**
- Core operations (arithmetic, logic, bitwise)
- Variable operations (load, save, set)
- Field operations (object fields)
- Type conversions
- Function calls
- Control flow (jumps, returns)
- String operations

**⚠️ Swapped/Renumbered: 6 opcodes**
- Comparison operators (CMPGR ↔ CMPLT, CMPGE ↔ CMPLE)
- Object operations (ADD_OBJECT, END_OBJECT renumbering)

**❌ Not in Scarface: 22 opcodes**
- Specialized returns (RETURN_VOID, RETURN_FLT, RETURN_UINT)
- Increment/decrement (INC, DEC)
- Variable lookup variants
- Internal object operations
- Typed push operations
- Iterator operations (ITER_BEGIN, ITER, ITER_END)
- Assertions and breakpoints
- Documentation strings

**🔧 Workarounds Needed: 3 features**
1. **OP_INC/OP_DEC**: Replace with LOAD + ADD/SUB + SAVE sequence
2. **foreach loops**: Not supported, use for loops instead
3. **Typed push**: Use generic OP_PUSH with type conversions

### 5.3 Opcode Translation Map

```cpp
// Torque3D opcode → Scarface opcode mapping
const U8 OPCODE_MAP_T3D_TO_SCARFACE[109] = {
    0,    // OP_FUNC_DECL → OP_FUNC_DECL
    1,    // OP_CREATE_OBJECT → OP_CREATE_OBJECT
    0xFF, // OP_ADD_OBJECT → NO DIRECT MAP (use workaround)
    0xFF, // OP_END_OBJECT → NO DIRECT MAP (use workaround)
    4,    // OP_FINISH_OBJECT → OP_ADD_OBJECT (renumbered)
    6,    // OP_JMPIFFNOT → OP_JMPIFFNOT
    7,    // OP_JMPIFNOT → OP_JMPIFNOT
    8,    // OP_JMPIFF → OP_JMPIFF
    9,    // OP_JMPIF → OP_JMPIF
    10,   // OP_JMPIFNOT_NP → OP_JMPIFNOT_NP
    11,   // OP_JMPIF_NP → OP_JMPIF_NP
    12,   // OP_JMP → OP_JMP
    13,   // OP_RETURN → OP_RETURN
    13,   // OP_RETURN_VOID → OP_RETURN (fallback)
    13,   // OP_RETURN_FLT → OP_RETURN (fallback)
    13,   // OP_RETURN_UINT → OP_RETURN (fallback)
    14,   // OP_CMPEQ → OP_CMPEQ
    17,   // OP_CMPGR → OP_CMPGR (Scarface #17, SWAPPED!)
    18,   // OP_CMPGE → OP_CMPGE (Scarface #18, SWAPPED!)
    15,   // OP_CMPLT → OP_CMPLT (Scarface #15, SWAPPED!)
    16,   // OP_CMPLE → OP_CMPLE (Scarface #16, SWAPPED!)
    19,   // OP_CMPNE → OP_CMPNE
    20,   // OP_XOR → OP_XOR
    21,   // OP_MOD → OP_MOD
    22,   // OP_BITAND → OP_BITAND
    23,   // OP_BITOR → OP_BITOR
    24,   // OP_NOT → OP_NOT
    25,   // OP_NOTF → OP_NOTF
    26,   // OP_ONESCOMPLEMENT → OP_ONESCOMPLEMENT
    27,   // OP_SHR → OP_SHR
    28,   // OP_SHL → OP_SHL
    29,   // OP_AND → OP_AND
    30,   // OP_OR → OP_OR
    31,   // OP_ADD → OP_ADD
    32,   // OP_SUB → OP_SUB
    33,   // OP_MUL → OP_MUL
    34,   // OP_DIV → OP_DIV
    35,   // OP_NEG → OP_NEG
    0xFF, // OP_INC → NOT SUPPORTED (use workaround)
    0xFF, // OP_DEC → NOT SUPPORTED (use workaround)
    36,   // OP_SETCURVAR → OP_SETCURVAR
    37,   // OP_SETCURVAR_CREATE → OP_SETCURVAR_CREATE
    38,   // OP_SETCURVAR_ARRAY → OP_SETCURVAR_ARRAY
    0xFF, // OP_SETCURVAR_ARRAY_VARLOOKUP → NOT SUPPORTED
    39,   // OP_SETCURVAR_ARRAY_CREATE → OP_SETCURVAR_ARRAY_CREATE
    0xFF, // OP_SETCURVAR_ARRAY_CREATE_VARLOOKUP → NOT SUPPORTED
    40,   // OP_LOADVAR_UINT → OP_LOADVAR_UINT
    41,   // OP_LOADVAR_FLT → OP_LOADVAR_FLT
    42,   // OP_LOADVAR_STR → OP_LOADVAR_STR
    0xFF, // OP_LOADVAR_VAR → NOT SUPPORTED
    43,   // OP_SAVEVAR_UINT → OP_SAVEVAR_UINT
    44,   // OP_SAVEVAR_FLT → OP_SAVEVAR_FLT
    45,   // OP_SAVEVAR_STR → OP_SAVEVAR_STR
    0xFF, // OP_SAVEVAR_VAR → NOT SUPPORTED
    46,   // OP_SETCUROBJECT → OP_SETCUROBJECT
    47,   // OP_SETCUROBJECT_NEW → OP_SETCUROBJECT_NEW
    0xFF, // OP_SETCUROBJECT_INTERNAL → NOT SUPPORTED
    48,   // OP_SETCURFIELD → OP_SETCURFIELD
    49,   // OP_SETCURFIELD_ARRAY → OP_SETCURFIELD_ARRAY
    0xFF, // OP_SETCURFIELD_TYPE → NOT SUPPORTED
    0xFF, // OP_SETCURFIELD_ARRAY_VAR → NOT SUPPORTED
    0xFF, // OP_SETCURFIELD_THIS → NOT SUPPORTED
    50,   // OP_LOADFIELD_UINT → OP_LOADFIELD_UINT
    51,   // OP_LOADFIELD_FLT → OP_LOADFIELD_FLT
    52,   // OP_LOADFIELD_STR → OP_LOADFIELD_STR
    53,   // OP_SAVEFIELD_UINT → OP_SAVEFIELD_UINT
    54,   // OP_SAVEFIELD_FLT → OP_SAVEFIELD_FLT
    55,   // OP_SAVEFIELD_STR → OP_SAVEFIELD_STR
    56,   // OP_STR_TO_UINT → OP_STR_TO_UINT
    57,   // OP_STR_TO_FLT → OP_STR_TO_FLT
    58,   // OP_STR_TO_NONE → OP_STR_TO_NONE
    59,   // OP_FLT_TO_UINT → OP_FLT_TO_UINT
    60,   // OP_FLT_TO_STR → OP_FLT_TO_STR
    61,   // OP_FLT_TO_NONE → OP_FLT_TO_NONE
    62,   // OP_UINT_TO_FLT → OP_UINT_TO_FLT
    63,   // OP_UINT_TO_STR → OP_UINT_TO_STR
    64,   // OP_UINT_TO_NONE → OP_UINT_TO_NONE
    0xFF, // OP_COPYVAR_TO_NONE → NOT SUPPORTED
    65,   // OP_LOADIMMED_UINT → OP_LOADIMMED_UINT
    66,   // OP_LOADIMMED_FLT → OP_LOADIMMED_FLT
    67,   // OP_TAG_TO_STR → OP_TAG_TO_STR
    68,   // OP_LOADIMMED_STR → OP_LOADIMMED_STR
    0xFF, // OP_DOCBLOCK_STR → NOT SUPPORTED
    69,   // OP_LOADIMMED_IDENT → OP_LOADIMMED_IDENT
    70,   // OP_CALLFUNC_RESOLVE → OP_CALLFUNC_RESOLVE
    71,   // OP_CALLFUNC → OP_CALLFUNC
    0xFF, // OP_CALLFUNC_POINTER → NOT SUPPORTED
    0xFF, // OP_CALLFUNC_THIS → NOT SUPPORTED
    72,   // OP_ADVANCE_STR → OP_ADVANCE_STR
    73,   // OP_ADVANCE_STR_APPENDCHAR → OP_ADVANCE_STR_APPENDCHAR
    74,   // OP_ADVANCE_STR_COMMA → OP_ADVANCE_STR_COMMA
    75,   // OP_ADVANCE_STR_NUL → OP_ADVANCE_STR_NUL
    76,   // OP_REWIND_STR → OP_REWIND_STR
    77,   // OP_TERMINATE_REWIND_STR → OP_TERMINATE_REWIND_STR
    78,   // OP_COMPARE_STR → OP_COMPARE_STR
    79,   // OP_PUSH → OP_PUSH
    79,   // OP_PUSH_UINT → OP_PUSH (use generic)
    79,   // OP_PUSH_FLT → OP_PUSH (use generic)
    79,   // OP_PUSH_VAR → OP_PUSH (use generic)
    0xFF, // OP_PUSH_THIS → NOT SUPPORTED
    80,   // OP_PUSH_FRAME → OP_PUSH_FRAME
    0xFF, // OP_ASSERT → NOT SUPPORTED
    0xFF, // OP_BREAK → NOT SUPPORTED
    0xFF, // OP_ITER_BEGIN → NOT SUPPORTED
    0xFF, // OP_ITER_BEGIN_STR → NOT SUPPORTED
    0xFF, // OP_ITER → NOT SUPPORTED
    0xFF, // OP_ITER_END → NOT SUPPORTED
    0xFF  // OP_INVALID → NOT SUPPORTED
};
```

**End of Part 2** - File size: ~48KB

Continue to **Part 3** for:
- Compiler Modifications Required
- Implementation Strategy
- Complete Code Examples
