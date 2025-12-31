# cameras.cso Array Pattern - Deep Investigation

**Target:** `stxnfojdoam["StuntCamInit", "CamOffset"] = "0.0 0.0 0.0";`  
**Location:** Line 106 (top-level, between functions)  
**Status:** SEARCHING FOR PATTERN

---

## Critical Discovery: Strings NOT in Bytecode!

### Search Results
- ❌ `stxnfojdoam` (offset 1020) - NOT found in bytecode
- ❌ `StuntCamInit` (offset 1032) - NOT found in bytecode
- ✅ `CamOffset` (offset 1045) - In GLOBAL strings
- ✅ `CamOffset` (offset 531) - ALSO in FUNCTION strings!

**Implication:** The array object name and index are NOT loaded with OP_LOADIMMED_IDENT!

---

## Function Structure Analysis

### Function 1: stxdakepcnn()
- Starts: Code 0
- Ends: Code 235 (end_idx = 235)
- Type: Simple field assignments

### Function 2: stxmdbdafgm()
- Starts: Code 235
- end_idx = 255 (0xFF - suspicious!)
- argc = 175 (0xAF - impossible!)

**Problem:** Second function's argc field shows 175 parameters, which is impossible!

**Hypothesis:** Maybe when end_idx > 255, it uses 2 bytes instead of 1?

OR: Maybe functions with many codes use an extended format?

---

## Bytecode at Code 255

```
Code 255: 0x00  → OP_FUNC_DECL (THIRD function!)
```

So there are AT LEAST 3 functions before the array assignments!

---

## Alternative Theory: Not Array Syntax?

**Question:** Maybe BrokenFace is MISINTERPRETING the bytecode?

Lines 106-109 show:
```torquescript
stxnfojdoam["StuntCamInit", "CamOffset"] = "0.0 0.0 0.0";
stxnfojdoam["StuntCamInit", "TargetOffset"] = "0.0 0.0 0.0";
stxnfojdoam["StuntCamInit", "FOV"] = "75";
stxfalgmdip["StuntCam", "0"] = "StuntCamInit Init_TargetObject 3000 1 false";
```

These might NOT be actual TorqueScript array syntax! They might be:
1. Function calls that LOOK like arrays
2. Special initialization syntax
3. Data table definitions
4. Macro expansions

---

## Next Steps

### 1. Find ALL Functions ⏳
Count total functions in cameras.cso to find where top-level code actually starts

### 2. Check Alternative Syntax ⏳
Search for "new" or other object creation patterns that might explain this

### 3. Compare with Mission Manager ⏳
Mission manager DEFINITELY has array syntax inside functions (line 238+)
That might be more straightforward than top-level

### 4. Check BrokenFace Limitations ⏳
Maybe BrokenFace can't handle certain patterns and outputs fake array syntax

---

## What We Know Works ✅

**Simple field access:**
```torquescript
object.field = value;
```

**Bytecode:**
```
OP_LOADIMMED_IDENT offset  → object name
OP_SETCUROBJECT            → select object
OP_SETCURFIELD offset      → field name
OP_LOADIMMED_STR offset    → value
OP_SAVEFIELD_STR           → save
```

---

## Status

**Understanding:** 30%  
**Next Action:** Count all functions, find actual top-level code  
**Confidence:** Medium - Pattern exists somewhere, just haven't found it yet

**Time Invested:** 4+ hours  
**Estimated Remaining:** 2-3 hours to find pattern
