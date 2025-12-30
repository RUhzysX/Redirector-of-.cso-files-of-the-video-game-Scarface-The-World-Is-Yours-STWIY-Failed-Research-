# Torque3D Engine Analysis & Scarface Compiler Guide - Part 1
### Complete Technical Documentation for Creating a Scarface-Compatible Compiler

**Version 1.0 - December 29, 2025**

---

## Table of Contents

**Part 1: Foundation & Architecture**
1. [Executive Summary](#1-executive-summary)
2. [Torque3D Engine Architecture](#2-torque3d-engine-architecture)
3. [TorqueScript Compilation Pipeline](#3-torquescript-compilation-pipeline)

**Part 2: File Formats & Opcodes** (See Part 2)
4. DSO File Format Specification
5. Opcode Comparison: Torque3D vs Scarface
6. Compiler Modifications Required

**Part 3: Implementation** (See Part 3)
7. Implementation Strategy
8. Code Modifications Guide
9. Building the Modified Compiler

**Part 4: Testing & Advanced** (See Part 4)
10. Testing & Validation
11. Advanced Topics
12. Appendices

---

## 1. Executive Summary

### 1.1 Project Goal

Create a modified Torque3D compiler that can compile TorqueScript (.cs) files into Scarface-compatible DSO/CSO bytecode format. This enables modders to write new scripts for Scarface: The World Is Yours using modern tooling and documentation.

### 1.2 Key Findings Summary

**Torque3D (Open Source - 2022)**
- 95 opcodes (OP_FUNC_DECL through OP_INVALID)
- Uses F64 (double precision) for all float operations
- Comprehensive string table system with deduplication
- Full 32-bit architecture with 64-bit pointer support
- Includes modern opcodes: iterator support, typed returns, assertions
- Advanced push opcodes for different data types
- Complete debugging information (line breaks, breakpoints)

**Scarface Variant (2006)**
- 86 opcodes total (numbered 0-85)
- Uses F32 (single precision) for float operations
- Hash-based string keys using custom MakeKey() function
- 32-bit architecture only, no 64-bit support
- Missing newer opcodes (iterators, specialized returns, etc.)
- Simpler opcode set focused on core game functionality
- No debugging information in compiled format
- Some opcodes have different interpretations/ordering

### 1.3 Compatibility Analysis

**Core Compatibility: ~85%**

The engines share the same lineage (Torque Game Engine), so the fundamental architecture is very similar. However, specific modifications are required:

**Required Changes:**
1. ✅ Remove/stub 22 newer opcodes not in Scarface
2. ✅ Convert all float operations from F64 → F32
3. ✅ Implement Scarface's hash function for string keys
4. ✅ Adjust bytecode compression (0xFF marker system differs)
5. ✅ Remove all debug information (line breaks, breakpoints)
6. ✅ Change version header and file format
7. ✅ Modify float table format (count vs byte size)

**Effort Estimate:**
- Core modifications: 2-3 weeks
- Testing & validation: 1-2 weeks
- Integration & documentation: 1 week
- **Total: 4-6 weeks for experienced C++ developer**

### 1.4 Why This Approach Works

**Advantages:**
- ✅ Start with battle-tested, well-documented code
- ✅ Full parser and AST already implemented
- ✅ Comprehensive optimization passes
- ✅ Active community support
- ✅ MIT licensed (can be modified freely)
- ✅ Cross-platform support (Windows, Linux, macOS)
- ✅ Modern C++ codebase (C++11/14)

**Challenges:**
- ⚠️ Need to carefully map opcodes
- ⚠️ Float precision loss when converting F64→F32
- ⚠️ Some language features won't be available
- ⚠️ Testing requires Scarface game or emulator

---

## 2. Torque3D Engine Architecture

### 2.1 High-Level System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                       Torque3D Engine                            │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │              Console System (TorqueScript)                   ││
│  │                                                              ││
│  │  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐   ││
│  │  │   Lexer      │ → │   Parser     │ → │  Compiler    │   ││
│  │  │  (CMDscan)   │   │ (AST Builder)│   │ (Bytecode)   │   ││
│  │  └──────────────┘   └──────────────┘   └──────────────┘   ││
│  │         ↓                   ↓                   ↓           ││
│  │  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐   ││
│  │  │  Token       │   │  AST Nodes   │   │  CodeBlock   │   ││
│  │  │  Stream      │   │  (ast.h)     │   │(codeBlock.h) │   ││
│  │  └──────────────┘   └──────────────┘   └──────────────┘   ││
│  │                                                 ↓           ││
│  │                                         ┌──────────────┐   ││
│  │                                         │ Interpreter  │   ││
│  │                                         │   (VM)       │   ││
│  │                                         └──────────────┘   ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                   SimObject System                           ││
│  │  • SimObject (base class for all game objects)              ││
│  │  • ScriptObject (objects defined in script)                 ││
│  │  • SimSet, SimGroup (containers)                            ││
│  │  • Namespace management                                     ││
│  │  • Field/Property system                                    ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │              Resource Management Layer                       ││
│  │  • FileStream (binary file I/O)                             ││
│  │  • ResManager (resource loading)                            ││
│  │  • StringTable (string interning)                           ││
│  │  • Memory management                                        ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Directory Structure

```
Torque3D/
├── Engine/
│   ├── source/
│   │   ├── console/                  ← TorqueScript system (PRIMARY)
│   │   │   ├── compiler.h            ← Opcode definitions
│   │   │   ├── compiler.cpp          ← Compilation tables
│   │   │   ├── codeBlock.h           ← CodeBlock structure
│   │   │   ├── codeBlock.cpp         ← DSO read/write (CRITICAL!)
│   │   │   ├── codeInterpreter.h     ← VM interface
│   │   │   ├── codeInterpreter.cpp   ← Opcode execution (CRITICAL!)
│   │   │   ├── ast.h                 ← Abstract syntax tree
│   │   │   ├── astNodes.cpp          ← AST node implementations
│   │   │   ├── CMDscan.cpp           ← Lexer/tokenizer
│   │   │   ├── consoleParser.h       ← Parser interface
│   │   │   ├── simObject.h           ← Base object class
│   │   │   ├── simObject.cpp         ← Object implementation
│   │   │   └── ...
│   │   │
│   │   ├── core/                     ← Core utilities
│   │   │   ├── stream/               ← File I/O
│   │   │   ├── strings/              ← String utilities
│   │   │   └── util/                 ← General utilities
│   │   │
│   │   ├── platform/                 ← Platform abstraction
│   │   │   ├── platform.h
│   │   │   ├── platformMemory.h
│   │   │   └── ...
│   │   │
│   │   ├── math/                     ← Math library
│   │   └── sim/                      ← Simulation system
│   │
│   ├── lib/                          ← Static libraries
│   └── bin/                          ← Executables
│
└── Tools/
    ├── projectGenerator/             ← Build system generator
    └── CMake/                        ← CMake scripts
```

### 2.3 Key Files for Modification

| File | Location | Purpose | Modification Priority | Complexity |
|------|----------|---------|----------------------|------------|
| `compiler.h` | console/ | Opcode enum definitions | **CRITICAL** | Medium |
| `compiler.cpp` | console/ | Compilation tables | **HIGH** | Medium |
| `codeBlock.h` | console/ | CodeBlock structure | **HIGH** | Low |
| `codeBlock.cpp` | console/ | DSO read/write | **CRITICAL** | High |
| `codeInterpreter.cpp` | console/ | VM execution | **HIGH** | High |
| `ast.h` | console/ | AST node types | **MODERATE** | Medium |
| `astNodes.cpp` | console/ | AST compilation | **MODERATE** | High |
| `stream.h` | core/stream/ | File I/O | **LOW** | Low |

### 2.4 Compilation Data Structures

#### CodeBlock Class

The `CodeBlock` class is the central structure representing compiled script code:

```cpp
class CodeBlock {
public:
    // File identification
    StringTableEntry name;              // Script filename (e.g., "script.cs")
    StringTableEntry fullPath;          // Full path to source file
    StringTableEntry modPath;           // Module path
    
    // String tables (two separate tables)
    char* globalStrings;                // Global scope string literals
    char* functionStrings;              // Function scope string literals
    U32 globalStringsMaxLen;            // Size of global table
    U32 functionStringsMaxLen;          // Size of function table
    
    // Float tables (CRITICAL: F64 in T3D, F32 in Scarface!)
    F64* globalFloats;                  // Global scope float constants
    F64* functionFloats;                // Function scope float constants
    
    // Bytecode
    U32 codeSize;                       // Number of U32 instructions
    U32* code;                          // Bytecode array
    
    // Debug information (NOT in Scarface!)
    U32 refCount;                       // Reference count
    U32 lineBreakPairCount;             // Number of line mappings
    U32* lineBreakPairs;                // Line number to IP mappings
    U32 breakListSize;                  // Breakpoint list size
    U32* breakList;                     // Active breakpoints
    
    // Linked list for all loaded code blocks
    CodeBlock* nextFile;
    
    // Key methods
    bool read(StringTableEntry fileName, Stream& st);
    bool compile(const char* dsoName, StringTableEntry fileName, 
                 const char* script, bool overrideNoDso = false);
    ConsoleValueRef exec(U32 offset, const char* fnName, 
                         Namespace* ns, U32 argc, 
                         ConsoleValueRef* argv, bool noCalls, 
                         StringTableEntry packageName, S32 setFrame = -1);
};
```

**Key Observations:**
1. **Dual String Tables**: Separate tables for global and function scope
2. **Float Storage**: Uses F64 arrays (need to convert to F32 for Scarface)
3. **Debug Info**: Line break pairs not needed for Scarface
4. **Reference Counting**: Memory management for loaded code

---

## 3. TorqueScript Compilation Pipeline

### 3.1 Complete Compilation Flow

```
┌──────────────────────────────────────────────────────────────────┐
│                    Source to Bytecode Pipeline                    │
└──────────────────────────────────────────────────────────────────┘

script.cs (Plain Text Source)
    │
    ↓
┌─────────────────────────────────────┐
│  STAGE 1: Lexical Analysis          │
│  File: CMDscan.cpp                   │
│                                      │
│  • Read source file                  │
│  • Handle UTF-8 BOM if present       │
│  • Tokenize into lexemes             │
│  • Recognize keywords, operators     │
│  • Handle string literals            │
│  • Track line numbers                │
│                                      │
│  Output: Token Stream                │
└─────────────────────────────────────┘
    │
    ↓
┌─────────────────────────────────────┐
│  STAGE 2: Syntax Analysis            │
│  File: ConsoleParser                 │
│                                      │
│  • Parse token stream                │
│  • Build Abstract Syntax Tree (AST)  │
│  • Validate syntax                   │
│  • Check grammar rules               │
│  • Report syntax errors              │
│                                      │
│  Output: AST (Statement Nodes)       │
└─────────────────────────────────────┘
    │
    ↓
┌─────────────────────────────────────┐
│  STAGE 3: Semantic Analysis          │
│  File: astNodes.cpp                  │
│                                      │
│  • Type checking                     │
│  • Variable scope resolution         │
│  • Function signature validation     │
│  • Namespace resolution              │
│                                      │
│  Output: Validated AST               │
└─────────────────────────────────────┘
    │
    ↓
┌─────────────────────────────────────┐
│  STAGE 4: Code Generation            │
│  File: astNodes.cpp (compile methods)│
│                                      │
│  • Traverse AST                      │
│  • Emit opcodes                      │
│  • Build string tables               │
│  • Build float tables                │
│  • Track identifiers                 │
│  • Generate jump targets             │
│                                      │
│  Output: CodeStream                  │
└─────────────────────────────────────┘
    │
    ↓
┌─────────────────────────────────────┐
│  STAGE 5: Optimization               │
│  File: compiler.cpp                  │
│                                      │
│  • Constant folding                  │
│  • Dead code elimination             │
│  • String deduplication              │
│  • Bytecode compression              │
│  • Jump optimization                 │
│                                      │
│  Output: Optimized Code              │
└─────────────────────────────────────┘
    │
    ↓
┌─────────────────────────────────────┐
│  STAGE 6: Serialization              │
│  File: codeBlock.cpp (compile method)│
│                                      │
│  • Write version header              │
│  • Write string tables               │
│  • Write float tables                │
│  • Write compressed bytecode         │
│  • Write identifier table            │
│  • Write debug info (if enabled)     │
│                                      │
│  Output: .dso/.cso Binary File       │
└─────────────────────────────────────┘
    │
    ↓
script.dso (Compiled Bytecode)
```

### 3.2 Compilation Tables in Detail

#### String Table (CompilerStringTable)

Manages all string literals in the script:

```cpp
struct CompilerStringTable {
    U32 totalLen;                       // Total buffer length needed
    
    struct Entry {
        char* string;                   // The actual string
        U32 start;                      // Offset in final buffer
        U32 len;                        // Length including null terminator
        bool tag;                       // Is this a tagged string?
        Entry* next;                    // Linked list pointer
    };
    Entry* list;                        // Entry linked list
    
    char buf[256];                      // Temporary formatting buffer
    std::unordered_map<std::string, Entry*> hashTable;  // Fast lookup
    
    // Add string, returns offset in table
    U32 add(const char* str, bool caseSens = true, bool tag = false);
    
    // Add numeric strings
    U32 addIntString(U32 value);
    U32 addFloatString(F64 value);
    
    // Build final linear buffer
    char* build();
    
    // Write to stream
    void write(Stream& st);
    
    // Clear for next compilation
    void reset();
};
```

**How it works:**
1. During compilation, every string literal calls `add()`
2. Hash table checks if string already exists
3. If exists, returns existing offset (deduplication!)
4. If new, adds to linked list and returns new offset
5. At end, `build()` creates linear character array
6. Bytecode references strings by offset into this array

**Example:**
```torquescript
echo("Hello");
echo("World");
echo("Hello");  // Reuses offset from first "Hello"!
```

String table will contain: `"Hello\0World\0"` (12 bytes total)
- First echo: offset 0
- Second echo: offset 6
- Third echo: offset 0 (reused!)

#### Float Table (CompilerFloatTable)

Manages all floating-point constants:

```cpp
struct CompilerFloatTable {
    struct Entry {
        F64 val;                        // Float value (64-bit in T3D!)
        Entry* next;                    // Linked list pointer
    };
    U32 count;                          // Number of entries
    Entry* list;                        // Entry linked list
    
    // Add float, returns index
    U32 add(F64 value);
    
    // Build array
    F64* build();
    
    // Write to stream
    void write(Stream& st);
    
    // Clear for next compilation
    void reset();
};
```

**Critical for Scarface:**
- Torque3D uses F64 (8 bytes per float)
- Scarface uses F32 (4 bytes per float)
- Must convert during write: `F32 val = (F32)floatTable[i];`
- Also, format difference: T3D writes byte size, Scarface writes count

**Example:**
```torquescript
%pi = 3.14159;
%e = 2.71828;
%area = %pi * 5.0 * 5.0;
```

Float table will contain: `[3.14159, 2.71828, 5.0]` (3 entries)
Bytecode references: OP_LOADIMMED_FLT [index 0] loads 3.14159

#### Identifier Table (CompilerIdentTable)

Tracks where identifiers are used in bytecode for patching:

```cpp
struct CompilerIdentTable {
    struct Entry {
        U32 offset;                     // Offset in string table
        U32 ip;                         // Instruction pointer
        Entry* next;                    // Next usage of same ident
        Entry* nextIdent;               // Next different ident
    };
    Entry* list;
    
    // Record identifier usage
    void add(StringTableEntry ste, U32 ip);
    
    // Write table for runtime patching
    void write(Stream& st);
    
    void reset();
};
```

**Purpose:**
At runtime, identifiers (variable names, function names) need to be resolved to actual StringTable entries. The ident table records all locations in bytecode where identifiers appear, so the loader can patch them with correct pointers.

**Example bytecode patch:**
```
Before loading:
  IP 42: OP_LOADIMMED_IDENT [string_offset: 15]

After loading:
  IP 42: OP_LOADIMMED_IDENT [StringTableEntry: 0x12345678]
```

### 3.3 CodeStream - Bytecode Emission

The `CodeStream` class emits bytecode during compilation:

```cpp
class CodeStream {
public:
    enum FixType {
        FIXTYPE_LOOPBLOCKSTART,    // Start of loop block
        FIXTYPE_BREAK,             // Break statement
        FIXTYPE_CONTINUE           // Continue statement
    };
    
    // Emit single instruction
    U32 emit(U32 code);
    
    // Emit string table entry (2 U32s on 64-bit)
    U32 emitSTE(const char* code);
    
    // Emit forward reference (for jumps)
    U32 emitFix(FixType type);
    
    // Patch previously emitted instruction
    void patch(U32 addr, U32 code);
    
    // Get current instruction pointer
    U32 tell();
    
    // Check if in loop context
    bool inLoop();
    
    // Scope management for fix-ups
    void pushFixScope(bool isLoop);
    void popFixScope();
    
    // Resolve loop jumps
    void fixLoop(U32 loopBlockStart, U32 breakPoint, U32 continuePoint);
    
    // Debug info
    void addBreakLine(U32 lineNumber, U32 ip);
    
    // Generate final code array
    void emitCodeStream(U32* size, U32** stream, U32** lineBreaks);
    
private:
    struct CodeData {
        U8* data;                   // Allocated block
        U32 size;                   // Bytes used
        CodeData* next;             // Next block
    };
    
    CodeData* mCode;                // Code blocks (linked list)
    U32 mCodePos;                   // Current position
    
    Vector<U32> mFixList;           // Forward references
    Vector<U32> mFixStack;          // Scope stack
    Vector<bool> mFixLoopStack;     // Loop context stack
    Vector<PatchEntry> mPatchList;  // Patches to apply
    Vector<U32> mBreakLines;        // Debug line mappings
};
```

**Emission Example:**

```cpp
// Compiling: %x = 5 + 3;

// 1. Load immediate 5
codeStream.emit(OP_LOADIMMED_UINT);
codeStream.emit(5);

// 2. Load immediate 3
codeStream.emit(OP_LOADIMMED_UINT);
codeStream.emit(3);

// 3. Add them
codeStream.emit(OP_ADD);

// 4. Set current variable to %x
codeStream.emit(OP_SETCURVAR_CREATE);
codeStream.emitSTE("x");  // Variable name

// 5. Save result
codeStream.emit(OP_SAVEVAR_UINT);
```

---

**End of Part 1** - File size: ~48KB

Continue to **Part 2** for:
- DSO File Format Specification
- Complete Opcode Comparison Table
- Compiler Modifications Required
