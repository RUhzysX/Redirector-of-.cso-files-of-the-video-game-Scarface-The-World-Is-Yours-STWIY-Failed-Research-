# Complete Array Pattern Analysis - Deep Dive

**Status:** IN PROGRESS - Deep analysis phase  
**Goal:** Understand array[index, field] = value pattern  
**Approach:** NO SHORTCUTS - Full analysis of real bytecode

---

## Files Analyzed (Full Deep Dive)

### 1. mission_manager.cso (86,252 bytes)
- **Pattern:** `stxcihoiagm[$stxlnifbepm, "Name"] = "FF_0";`
- **Location:** Line 15 (top-level, not in function)
- **Bytecode offset:** 104-125
- **Status:** Analyzed but pattern is complex

### 2. cameras.cso (13,606 bytes)
- **Pattern:** `stxnfojdoam["StuntCamInit", "CamOffset"] = "0.0 0.0 0.0";`
- **Location:** Line 106 (top-level, between functions)
- **Status:** Located, ready to analyze

---

## Key Discoveries from BrokenFace Source

### Discovery 1: OP_SETCUROBJECT Takes NO Parameters! ✅
```python
# BrokenFace codec.py line 1036-1037
def opSetcurobject(self):
    self.curobj = self.strStack[-1]  # Reads from STRING STACK!
```

**Impact:** Must load object name to stack FIRST with OP_LOADIMMED_IDENT

### Discovery 2: String Table Format ✅
**Strings are stored WITHOUT $ or % prefixes!**

Examples from mission_manager.cso:
- Offset 49: `stxlnifbepm` (not `$stxlnifbepm`)
- Offset 162: `stxcihoiagm` (not `$stxcihoiagm`)

BrokenFace ADDS prefixes during decompilation (codec.py lines 928-937)

### Discovery 3: Opcode Dispatch Table ✅
```python
# BrokenFace codec.py lines 1498-1505
36: opSetcurvar,              # OP_SETCURVAR
37: opSetcurvar,              # OP_SETCURVAR_CREATE
38: opSetcurvar,              # (same function!)
39: opSetcurvar,              # (same function!)
40: opSetcurvarArray,         # OP_SETCURVAR_ARRAY
41: opSetcurvarArray,         # OP_SETCURVAR_ARRAY_CREATE
42: opSetcurvarArray,         # (same function!)
43: opSetcurvarArray,         # (same function!)
```

**Key insight:** Multiple opcodes share the same handler function!

### Discovery 4: opSetcurvar DOES Take Parameters! ✅
```python
# BrokenFace codec.py lines 924-926
def opSetcurvar(self):
    offset = self.getStringOffset()  # Reads 2-byte offset!
    string = self.getGlobalStringByOffset(offset)
```

So opcodes 36-39 ALL take a 2-byte offset parameter.

### Discovery 5: opSetcurvarArray Implementation ✅
```python
# BrokenFace codec.py lines 948-949
def opSetcurvarArray(self):
    self.curvar = torque.ArrayAccess(self.strStack[-1])
```

Comment says "Retrieves the symbol and index from string stack"

**But:** Code only reads `strStack[-1]`!

**Question:** Does this read BOTH variable name AND index from a single stack element?

---

## Bytecode Patterns Analyzed

### Pattern A: Variable Initialization (mission_manager offset 0-103)
```
Every 8 bytes:
  0x45 value           → OP_LOADIMMED_UINT value
  0x27 0x00 0x00       → OP_SETCURVAR_ARRAY_CREATE offset=0
  0x2F                 → OP_SAVEVAR_FLT
  0x44                 → OP_TERMINATE_REWIND_STR
```

**Purpose:** Initialize global variables to 0, 1, 2, etc.

Example: `$stxoapcpagk = 0;`

### Pattern B: Array Assignment (mission_manager offset 104-125)
```
104: OP_LOADIMMED_IDENT 157    → Push "FF_0" to string stack
107: OP_ADVANCE_STR            → Advance string stack (new slot)
108: OP_SETCURVAR_CREATE 0     → Create variable from... what?
111: OP_ADVANCE_STR            → Advance again
112: OP_SETCURVAR 0            → Select variable at offset 0
115: OP_SAVEVAR_UINT           → Save uint to variable
116: OP_LOADVAR_STR            → Load variable back as string
117: OP_LOADIMMED_IDENT 174    → Push "Name" to string stack
120: OP_SETCUROBJECT_NEW (x2!) → Two calls!
121: OP_SETCUROBJECT_NEW       → Why twice?
122: OP_SAVEVAR_STR            → Save string to variable
123: OP_LOADFIELD_STR          → Load field as string
124: OP_SAVEFIELD_UINT         → Save uint to field
125: OP_STR_TO_NONE            → Clean up stack
```

**Expected:** `stxcihoiagm[$stxlnifbepm, "Name"] = "FF_0";`

**Problems:**
1. Where is `stxcihoiagm` (offset 162)?
2. Where is `$stxlnifbepm` (offset 49)?
3. Why two OP_SETCUROBJECT_NEW calls?
4. What is OP_ADVANCE_STR actually doing?

---

## String Stack Mechanics

### OP_ADVANCE_STR Analysis ✅
```python
# BrokenFace codec.py line 1369
def opAdvanceStr(self):
    self.strStack.advance()

# StringStack.advance() implementation (lines 14-30)
def advance(self, ch=None):
    if ch is not None:
        # Handle special characters (NL, TAB, SPC, comma, etc.)
    else:
        # No character - just push a new slot
        self.append(...)  # Exact impl not shown, but pushes new element
```

**Purpose:** String concatenation / building complex strings

**Hypothesis:** Used to build array access expressions like `array[index, field]`

---

## Current Understanding

### What I Know ✅
1. Simple field access works: `object.field = value`
2. String table format and prefix rules
3. OP_SETCUROBJECT behavior (reads from stack)
4. Opcode dispatch table structure
5. Variable initialization pattern

### What I Don't Know ⏳
1. How array object name is selected
2. How index variable is loaded
3. Why OP_SETCUROBJECT_NEW appears twice
4. Complete OP_ADVANCE_STR usage pattern
5. How OP_SETCURVAR_ARRAY actually works

---

## Hypothesis: Hidden Context

**Theory:** The array object and index might be set up BEFORE the pattern at offset 104!

**Evidence:**
- Pattern starts at offset 104
- Variable initializations end at offset 103
- No obvious array/index setup in 104-125 sequence

**Alternative Theory:** 
Maybe `stxcihoiagm` and `$stxlnifbepm` are ALREADY in the "current" state from previous operations, and the pattern at 104-125 is just setting the FIELD, not the array access itself!

---

## Next Steps (Priority Order)

### 1. Analyze Simpler Pattern ⏳
Use cameras.cso: `stxnfojdoam["StuntCamInit", "CamOffset"] = "0.0 0.0 0.0";`

**Advantages:**
- String literal indices (not variables)
- Top-level code
- Simpler context

### 2. Find Array Setup Code ⏳
Search mission_manager for where `stxcihoiagm` is first referenced

**Search for:**
- OP_LOADIMMED_IDENT 162 (stxcihoiagm)
- Any pattern that sets up array context

### 3. Test with BrokenFace Logging ⏳
Run BrokenFace with debug logging on cameras.cso to see:
- Exact execution order
- Stack contents at each step
- Variable states

### 4. Build Minimal Test Case ⏳
Create tiny TorqueScript with just:
```torquescript
obj[0, "field"] = "value";
```

Compile with real Torque3D compiler, compare bytecode

---

## Files to Analyze Next

### Priority 1: cameras.cso (ACTIVE)
**Pattern:** `stxnfojdoam["StuntCamInit", "CamOffset"] = "0.0 0.0 0.0";`
**String offsets:**
- 1020: stxnfojdoam (array)
- 1032: StuntCamInit (index)
- 1045: CamOffset (field)

**Action:** Find bytecode for line 106, decode full pattern

### Priority 2: defaultgame.cso
Has array patterns, might be simpler

### Priority 3: inventory.cso
Has array patterns, might be simpler

---

## Testing Strategy

### Phase 1: Understand (CURRENT)
- ✅ Analyze real bytecode
- ⏳ Map complete pattern
- ⏳ Understand all opcodes involved

### Phase 2: Replicate
- Create minimal test
- Generate bytecode
- Verify with BrokenFace

### Phase 3: Implement
- Add opcodes to compiler
- Build high-level helpers
- Test with real patterns

---

## Known Working Patterns

### Simple Field Access ✅
```torquescript
object.field = value;
```

**Bytecode:**
```
OP_LOADIMMED_IDENT offset  → Push object name
OP_SETCUROBJECT            → Select object (reads stack)
OP_SETCURFIELD offset      → Select field (takes offset)
OP_LOADIMMED_STR offset    → Push value
OP_SAVEFIELD_STR           → Save to field
```

**Status:** WORKING, verified with BrokenFace

---

## Estimated Completion

**Current Progress:** 60% understanding  
**Time to full understanding:** 2-4 hours more analysis  
**Time to implementation:** 1-2 hours  
**Total:** 3-6 hours to working array support

**Confidence:** HIGH - Methodology is solid, just need more data points

---

## Summary

**Achievements:**
- ✅ Fixed OP_SETCUROBJECT (no parameters!)
- ✅ Simple field access works
- ✅ Complete BrokenFace source analysis
- ✅ String table format understood
- ✅ Opcode dispatch table mapped

**Blockers:**
- ⏳ Need to understand complete array pattern
- ⏳ Missing array object setup mechanism
- ⏳ OP_ADVANCE_STR usage not clear

**Approach:**
- NO SHORTCUTS
- Full bytecode analysis
- Multiple file comparison
- Real pattern verification

**Status:** Making steady progress, pattern is complex but analyzable!
