# Mission Manager Array Pattern - Complete Analysis

**File:** mission_manager.cso (86,252 bytes)  
**Pattern:** `stxcihoiagm[$stxlnifbepm, "Name"] = "FF_0";`

---

## String Table References

### Global Strings (relevant)
- Offset 49: `stxlnifbepm` (NO $ prefix in table!)
- Offset 157: `FF_0` (value)
- Offset 162: `stxcihoiagm` (array name, NO $ prefix!)
- Offset 174: `Name` (field name)

### Key Discovery
**String table stores names WITHOUT $ or % prefixes!**
BrokenFace ADDS the prefix during decompilation based on context.

---

## Actual Bytecode Pattern (offset 104-125)

```
104: OP_LOADIMMED_IDENT 157    → Push "FF_0" to string stack
107: OP_ADVANCE_STR            → Advance string stack (push new slot)
108: OP_SETCURVAR_CREATE 0     → Create variable from... something?
111: OP_ADVANCE_STR            → Advance again
112: OP_SETCURVAR 0            → Select variable at offset 0
115: OP_SAVEVAR_UINT           → Save uint to variable
116: OP_LOADVAR_STR            → Load variable back as string
117: OP_LOADIMMED_IDENT 174    → Push "Name" to string stack
120: OP_SETCUROBJECT_NEW       → Select newly created object
121: OP_SETCUROBJECT_NEW       → (AGAIN?!)
122: OP_SAVEVAR_STR            → Save string to variable
123: OP_LOADFIELD_STR          → Load field as string
124: OP_SAVEFIELD_UINT         → Save uint to field  
125: OP_STR_TO_NONE            → Clean up stack
```

---

## Problems with This Pattern

1. **Where is `stxcihoiagm`?** The array name isn't in this sequence!
2. **Where is `$stxlnifbepm`?** The index variable isn't referenced!
3. **Two OP_SETCUROBJECT_NEW?** Why two in a row?
4. **OP_SETCURVAR offset 0?** What is at offset 0?

---

## Hypothesis: Looking at WRONG Section

The bytecode at offset 104-125 might NOT be the array assignment!

Let me check EARLIER in the bytecode for where array/index are set up.

### Before This Pattern (offset 0-103)

Earlier analysis showed:
```
0-95: Variable initializations
  $stxoapcpagk = 0;
  $stxajhnpmcn = 1;
  $stxpmgighdi = "";
  etc.
```

So by offset 104, all variables are already initialized.

---

## Alternative Theory: Context-Dependent Opcodes

Maybe the array/index were set as "current object" and "current index" BEFORE this pattern starts?

Looking at mission_manager decompiled:
```torquescript
$stxlnifbepm = 0;  // Line 5
...
stxcihoiagm[$stxlnifbepm, "Name"] = "FF_0";  // Line 15
```

So there are 10+ lines BETWEEN the index initialization and the array access!

---

## What OP_SETCURVAR_CREATE Offset 0 Means

Offset 0 in global string table is: `"stxoapcpagk"`

But wait, that's not relevant here!

Actually, when OP_SETCURVAR_CREATE has offset 0, and the string is empty `""` (at offset 24), maybe it's creating a TEMPORARY variable?

---

## Need to See FULL Context

The pattern at offset 104 is NOT self-contained. I need to see what happens from offset 0 to 200 as a complete sequence.

---

## Action Items

1. ⏳ Trace COMPLETE initialization sequence (offset 0-104)
2. ⏳ Find where `stxcihoiagm` is first referenced
3. ⏳ Find where `$stxlnifbepm` is used as index
4. ⏳ Understand OP_ADVANCE_STR usage
5. ⏳ Understand OP_SETCURVAR_CREATE with offset 0

---

## Status

**Current Understanding:** 10%  
**Confidence:** Low  
**Next Step:** Full 0-200 bytecode trace with ALL opcodes decoded

This pattern is MUCH more complex than simple field access!
