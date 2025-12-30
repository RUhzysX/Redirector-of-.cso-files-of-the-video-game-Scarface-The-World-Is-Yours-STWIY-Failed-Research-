# Torque3D Engine Analysis & Scarface Compiler Guide - Part 3
### Compiler Modifications & Implementation

**Continued from Part 2**

---

## 6. Compiler Modifications Required

### 6.1 Overview of Changes

**Priority Levels:**
- 🔴 **CRITICAL**: Must be done or compilation will fail
- 🟠 **HIGH**: Important for compatibility
- 🟡 **MODERATE**: Affects some scripts
- 🟢 **LOW**: Optional or minor impact

| Change | Priority | Files Affected | Estimated Time |
|--------|----------|----------------|----------------|
| Opcode enum modification | 🔴 CRITICAL | compiler.h | 2 hours |
| Float type conversion (F64→F32) | 🔴 CRITICAL | codeBlock.h/cpp | 4 hours |
| DSO write format | 🔴 CRITICAL | codeBlock.cpp | 6 hours |
| DSO read format | 🔴 CRITICAL | codeBlock.cpp | 4 hours |
| Remove debug info | 🟠 HIGH | codeBlock.cpp | 2 hours |
| Hash function implementation | 🟠 HIGH | New file | 3 hours |
| Opcode workarounds | 🟡 MODERATE | astNodes.cpp | 8 hours |
| Build configuration | 🟢 LOW | CMakeLists.txt | 1 hour |

**Total Estimated Time: ~30 hours** (3-4 days for experienced developer)

### 6.2 Critical Modification #1: Opcode Enumeration

**File:** `Engine/source/console/compiler.h`

**Before (Torque3D):**
```cpp
namespace Compiler {
    enum CompiledInstructions {
        OP_FUNC_DECL,
        OP_CREATE_OBJECT,
        OP_ADD_OBJECT,
        OP_END_OBJECT,
        OP_FINISH_OBJECT,        // ← Remove
        
        OP_JMPIFFNOT,
        // ... (95 total opcodes)
        
        OP_ITER_BEGIN,           // ← Remove
        OP_ITER_BEGIN_STR,       // ← Remove
        OP_ITER,                 // ← Remove
        OP_ITER_END,             // ← Remove
        OP_INVALID,              // ← Remove
        
        MAX_OP_CODELEN
    };
}
```

**After (Scarface-compatible):**
```cpp
namespace Compiler {
#ifdef SCARFACE_COMPATIBLE
    // Scarface opcode set (81 opcodes, 0-80)
    enum CompiledInstructions {
        OP_FUNC_DECL,                    // 0
        OP_CREATE_OBJECT,                // 1
        OP_2_CONTINUE,                   // 2 (Scarface specific)
        OP_3_CONTINUE,                   // 3 (Scarface specific)
        OP_ADD_OBJECT,                   // 4
        OP_END_OBJECT,                   // 5
        
        OP_JMPIFFNOT,                    // 6
        OP_JMPIFNOT,                     // 7
        OP_JMPIFF,                       // 8
        OP_JMPIF,                        // 9
        OP_JMPIFNOT_NP,                  // 10
        OP_JMPIF_NP,                     // 11
        OP_JMP,                          // 12
        OP_RETURN,                       // 13
        
        OP_CMPEQ,                        // 14
        OP_CMPLT,                        // 15 (SWAPPED in Scarface!)
        OP_CMPLE,                        // 16 (SWAPPED in Scarface!)
        OP_CMPGR,                        // 17 (SWAPPED in Scarface!)
        OP_CMPGE,                        // 18 (SWAPPED in Scarface!)
        OP_CMPNE,                        // 19
        
        OP_XOR,                          // 20
        OP_MOD,                          // 21
        OP_BITAND,                       // 22
        OP_BITOR,                        // 23
        OP_NOT,                          // 24
        OP_NOTF,                         // 25
        OP_ONESCOMPLEMENT,               // 26
        
        OP_SHR,                          // 27
        OP_SHL,                          // 28
        OP_AND,                          // 29
        OP_OR,                           // 30
        
        OP_ADD,                          // 31
        OP_SUB,                          // 32
        OP_MUL,                          // 33
        OP_DIV,                          // 34
        OP_NEG,                          // 35
        
        OP_SETCURVAR,                    // 36
        OP_SETCURVAR_CREATE,             // 37
        OP_SETCURVAR_ARRAY,              // 38
        OP_SETCURVAR_ARRAY_CREATE,       // 39
        
        OP_LOADVAR_UINT,                 // 40
        OP_LOADVAR_FLT,                  // 41
        OP_LOADVAR_STR,                  // 42
        
        OP_SAVEVAR_UINT,                 // 43
        OP_SAVEVAR_FLT,                  // 44
        OP_SAVEVAR_STR,                  // 45
        
        OP_SETCUROBJECT,                 // 46
        OP_SETCUROBJECT_NEW,             // 47
        
        OP_SETCURFIELD,                  // 48
        OP_SETCURFIELD_ARRAY,            // 49
        
        OP_LOADFIELD_UINT,               // 50
        OP_LOADFIELD_FLT,                // 51
        OP_LOADFIELD_STR,                // 52
        
        OP_SAVEFIELD_UINT,               // 53
        OP_SAVEFIELD_FLT,                // 54
        OP_SAVEFIELD_STR,                // 55
        
        OP_STR_TO_UINT,                  // 56
        OP_STR_TO_FLT,                   // 57
        OP_STR_TO_NONE,                  // 58
        OP_FLT_TO_UINT,                  // 59
        OP_FLT_TO_STR,                   // 60
        OP_FLT_TO_NONE,                  // 61
        OP_UINT_TO_FLT,                  // 62
        OP_UINT_TO_STR,                  // 63
        OP_UINT_TO_NONE,                 // 64
        
        OP_LOADIMMED_UINT,               // 65
        OP_LOADIMMED_FLT,                // 66
        OP_TAG_TO_STR,                   // 67
        OP_LOADIMMED_STR,                // 68
        OP_LOADIMMED_IDENT,              // 69
        
        OP_CALLFUNC_RESOLVE,             // 70
        OP_CALLFUNC,                     // 71
        
        OP_ADVANCE_STR,                  // 72
        OP_ADVANCE_STR_APPENDCHAR,       // 73
        OP_ADVANCE_STR_COMMA,            // 74
        OP_ADVANCE_STR_NUL,              // 75
        OP_REWIND_STR,                   // 76
        OP_TERMINATE_REWIND_STR,         // 77
        OP_COMPARE_STR,                  // 78
        
        OP_PUSH,                         // 79
        OP_PUSH_FRAME,                   // 80
        
        MAX_OP_CODELEN = 81              // 81 opcodes total
    };
#else
    // Standard Torque3D opcodes (unchanged)
    enum CompiledInstructions {
        // ... original T3D opcodes ...
    };
#endif
}
```

### 6.3 Critical Modification #2: Float Type

**File:** `Engine/source/console/codeBlock.h`

**Before:**
```cpp
class CodeBlock {
    // ...
    F64* globalFloats;          // 64-bit doubles
    F64* functionFloats;        // 64-bit doubles
    // ...
};
```

**After:**
```cpp
class CodeBlock {
    // ...
#ifdef SCARFACE_FLOAT_F32
    F32* globalFloats;          // 32-bit floats for Scarface
    F32* functionFloats;        // 32-bit floats for Scarface
#else
    F64* globalFloats;          // 64-bit doubles for T3D
    F64* functionFloats;        // 64-bit doubles for T3D
#endif
    // ...
};
```

**File:** `Engine/source/console/compiler.h`

Add type alias:
```cpp
namespace Compiler {
#ifdef SCARFACE_FLOAT_F32
    typedef F32 ScriptFloat;    // Use 32-bit for Scarface
#else
    typedef F64 ScriptFloat;    // Use 64-bit for T3D
#endif

    struct CompilerFloatTable {
        struct Entry {
            ScriptFloat val;     // Use typedef
            Entry* next;
        };
        U32 count;
        Entry* list;
        
        U32 add(ScriptFloat value);
        ScriptFloat* build();
        void write(Stream& st);
    };
}
```

### 6.4 Critical Modification #3: DSO Write Function

**File:** `Engine/source/console/codeBlock.cpp`

**Key changes in compile() method:**

```cpp
bool CodeBlock::compile(const char* codeFileName, 
                        StringTableEntry fileName, 
                        const char* inScript, 
                        bool overrideNoDso) {
    // ... parsing and compilation ...
    
    FileStream st;
    if (!st.open(codeFileName, Torque::FS::File::Write))
        return false;
    
#ifdef SCARFACE_COMPATIBLE
    // Write Scarface version (always 1)
    st.write(U32(1));
#else
    // Write Torque3D version
    st.write(U32(Con::DSOVersion));
#endif
    
    // Reset compilation tables
    resetTables();
    
    // ... compile AST to bytecode ...
    
    // Write global string table (same for both)
    getGlobalStringTable().write(st);
    
#ifdef SCARFACE_COMPATIBLE
    // SCARFACE: Write float COUNT, not byte size!
    CompilerFloatTable& globalFloats = getGlobalFloatTable();
    st.write(globalFloats.count);  // Count, not bytes!
    
    // Write as F32 values
    CompilerFloatTable::Entry* walk = globalFloats.list;
    for (U32 i = globalFloats.count; i > 0; i--) {
        F32 val = (F32)walk->val;  // Convert F64 → F32
        st.write(val);             // Write 4 bytes
        walk = walk->next;
    }
#else
    // TORQUE3D: Write byte size then F64 values
    getGlobalFloatTable().write(st);
#endif
    
    // Write function string table (same for both)
    getFunctionStringTable().write(st);
    
#ifdef SCARFACE_COMPATIBLE
    // SCARFACE: Write function float count and F32 values
    CompilerFloatTable& funcFloats = getFunctionFloatTable();
    st.write(funcFloats.count);
    walk = funcFloats.list;
    for (U32 i = funcFloats.count; i > 0; i--) {
        F32 val = (F32)walk->val;
        st.write(val);
        walk = walk->next;
    }
#else
    // TORQUE3D: Standard format
    getFunctionFloatTable().write(st);
#endif
    
    // Write code size
    st.write(codeSize);
    
#ifndef SCARFACE_NO_LINEBREAKS
    // Torque3D: Write line break count
    st.write(lineBreakPairCount);
#endif
    
    // Write compressed bytecode (same compression for both)
    for (U32 i = 0; i < codeSize; i++) {
        if (code[i] < 0xFF)
            st.write(U8(code[i]));
        else {
            st.write(U8(0xFF));
            st.write(code[i]);
        }
    }
    
#ifndef SCARFACE_NO_LINEBREAKS
    // Torque3D: Write line break pairs
    for (U32 i = codeSize; i < totSize; i++)
        st.write(code[i]);
#endif
    
    // Write identifier table (same for both)
    getIdentTable().write(st);
    
    st.close();
    return true;
}
```

### 6.5 Critical Modification #4: DSO Read Function

**File:** `Engine/source/console/codeBlock.cpp`

```cpp
bool CodeBlock::read(StringTableEntry fileName, Stream& st) {
    // ... path setup ...
    
    addToCodeList();
    
    U32 globalSize, size, i;
    
    // Read global string table (same for both)
    st.read(&size);
    if (size) {
        globalStrings = new char[size];
        globalStringsMaxLen = size;
        st.read(size, globalStrings);
    }
    globalSize = size;
    
#ifdef SCARFACE_COMPATIBLE
    // SCARFACE: Read float COUNT
    U32 floatCount;
    st.read(&floatCount);
    if (floatCount) {
        globalFloats = new F32[floatCount];
        for (i = 0; i < floatCount; i++) {
            F32 val;
            st.read(&val);
            globalFloats[i] = val;
        }
    }
#else
    // TORQUE3D: Read byte size, then F64 values
    st.read(&size);
    if (size) {
        globalFloats = new F64[size];
        for (i = 0; i < size; i++)
            st.read(&globalFloats[i]);
    }
#endif
    
    // Read function string table (same for both)
    st.read(&size);
    if (size) {
        functionStrings = new char[size];
        functionStringsMaxLen = size;
        st.read(size, functionStrings);
    }
    
#ifdef SCARFACE_COMPATIBLE
    // SCARFACE: Read function float count
    st.read(&floatCount);
    if (floatCount) {
        functionFloats = new F32[floatCount];
        for (i = 0; i < floatCount; i++) {
            F32 val;
            st.read(&val);
            functionFloats[i] = val;
        }
    }
#else
    // TORQUE3D: Read byte size, then F64 values
    st.read(&size);
    if (size) {
        functionFloats = new F64[size];
        for (i = 0; i < size; i++)
            st.read(&functionFloats[i]);
    }
#endif
    
    // Read bytecode
    U32 codeLength;
    st.read(&codeLength);
    
#ifndef SCARFACE_NO_LINEBREAKS
    st.read(&lineBreakPairCount);
    U32 totSize = codeLength + lineBreakPairCount * 2;
    code = new U32[totSize];
#else
    // SCARFACE: No line breaks in file
    code = new U32[codeLength];
#endif
    
    // Read compressed bytecode (same for both)
    for (i = 0; i < codeLength; i++) {
        U8 b;
        st.read(&b);
        if (b == 0xFF)
            st.read(&code[i]);
        else
            code[i] = b;
    }
    
#ifndef SCARFACE_NO_LINEBREAKS
    // TORQUE3D: Read line break pairs
    for (i = codeLength; i < totSize; i++)
        st.read(&code[i]);
    lineBreakPairs = code + codeLength;
    if (lineBreakPairCount)
        calcBreakList();
#endif
    
    // Read identifier table (same for both)
    U32 identCount;
    st.read(&identCount);
    while (identCount--) {
        U32 offset;
        st.read(&offset);
        StringTableEntry ste;
        if (offset < globalSize)
            ste = StringTable->insert(globalStrings + offset);
        else
            ste = StringTable->EmptyString();
        U32 count;
        st.read(&count);
        while (count--) {
            U32 ip;
            st.read(&ip);
#ifdef TORQUE_CPU_X64
            *(U64*)(code + ip) = (U64)ste;
#else
            code[ip] = *((U32*)&ste);
#endif
        }
    }
    
    return true;
}
```

### 6.6 New File: Scarface Hash Functions

**File:** `Engine/source/console/scarfaceHash.h` (NEW)

```cpp
#ifndef _SCARFACE_HASH_H_
#define _SCARFACE_HASH_H_

#include "platform/platform.h"

namespace Scarface {

/**
 * Scarface's string hash function (MakeKey)
 * Algorithm: Multiplicative hash with XOR
 */
inline U32 MakeKey(const char* str) {
    U32 key = 0;
    while (*str) {
        key *= 65599;
        key = key ^ static_cast<U32>(*str);
        str++;
    }
    return key;
}

/**
 * Convert hash to string representation: "stxXXXXXXXX"
 * Format: 2 chars per byte, little-endian
 */
inline const char* KeyToString(U32 key) {
    static char buffer[12];
    buffer[0] = 's';
    buffer[1] = 't';
    buffer[2] = 'x';
    
    for (int i = 0; i < 4; ++i) {
        U8 byte = reinterpret_cast<U8*>(&key)[i];
        int index = 3 + (i << 1);
        buffer[index] = 'a' + (byte & 0x0F);
        buffer[index + 1] = 'a' + (byte >> 4);
    }
    
    buffer[11] = '\0';
    return buffer;
}

/**
 * Parse string hash back to key
 * Input: "stxXXXXXXXX" format
 */
inline U32 StringKeyToKey(const char* str) {
    if (!str || str[0] != 's' || str[1] != 't' || str[2] != 'x')
        return 0xFFFFFFFF;
    
    U32 key = 0;
    U8* bytes = reinterpret_cast<U8*>(&key);
    
    for (int i = 0; i < 4; ++i) {
        int index = 3 + (i << 1);
        U8 low = str[index] - 'a';
        U8 high = str[index + 1] - 'a';
        bytes[i] = (high << 4) | low;
    }
    
    return key;
}

/**
 * Test if string is hash format
 */
inline bool isHashString(const char* str) {
    return str && str[0] == 's' && str[1] == 't' && str[2] == 'x';
}

} // namespace Scarface

#endif // _SCARFACE_HASH_H_
```

### 6.7 Opcode Workarounds

**File:** `Engine/source/console/astNodes.cpp`

Handle removed opcodes with workarounds:

```cpp
// Increment operator workaround
void IntUnaryExprNode::compile(U32& ip, CodeStream& codeStream) {
    if (op == opPlusPlus) {
#ifdef SCARFACE_COMPATIBLE
        // Scarface doesn't have OP_INC, so:
        // 1. Load variable
        expr->compile(ip, codeStream);
        // 2. Add 1
        codeStream.emit(OP_LOADIMMED_UINT);
        codeStream.emit(1);
        codeStream.emit(OP_ADD);
        // 3. Save back
        expr->compileStore(ip, codeStream);
#else
        expr->compile(ip, codeStream);
        codeStream.emit(OP_INC);
#endif
    }
    else if (op == opMinusMinus) {
#ifdef SCARFACE_COMPATIBLE
        // Similar workaround for decrement
        expr->compile(ip, codeStream);
        codeStream.emit(OP_LOADIMMED_UINT);
        codeStream.emit(1);
        codeStream.emit(OP_SUB);
        expr->compileStore(ip, codeStream);
#else
        expr->compile(ip, codeStream);
        codeStream.emit(OP_DEC);
#endif
    }
}

// Foreach loop unsupported
void IterNode::compile(U32& ip, CodeStream& codeStream) {
#ifdef SCARFACE_COMPATIBLE
    Con::errorf("foreach loops are not supported in Scarface mode");
    Con::errorf("Use traditional for loops instead");
    return;
#else
    // Normal foreach compilation
    codeStream.emit(OP_ITER_BEGIN);
    // ... rest of implementation ...
#endif
}

// Typed push workaround
void FunctionCallExprNode::compileArgs(U32& ip, CodeStream& codeStream) {
    // Compile each argument
    for (ExprNode* arg = args; arg; arg = arg->next) {
        arg->compile(ip, codeStream);
        
#ifdef SCARFACE_COMPATIBLE
        // Always use generic OP_PUSH
        codeStream.emit(OP_PUSH);
#else
        // Use typed push if available
        if (arg->type == TypeU32)
            codeStream.emit(OP_PUSH_UINT);
        else if (arg->type == TypeF32)
            codeStream.emit(OP_PUSH_FLT);
        else
            codeStream.emit(OP_PUSH);
#endif
    }
    
    codeStream.emit(OP_PUSH_FRAME);
}
```

---

## 7. Implementation Strategy

### 7.1 Development Roadmap

**Week 1: Setup & Core Changes**
- Day 1-2: Set up build environment, create Scarface branch
- Day 3-4: Implement opcode enum modifications
- Day 5: Implement float type changes (F64→F32)

**Week 2: File Format**
- Day 1-2: Modify DSO write function
- Day 3-4: Modify DSO read function
- Day 5: Testing with simple scripts

**Week 3: Opcode Workarounds**
- Day 1-2: Implement increment/decrement workarounds
- Day 3: Handle foreach loops
- Day 4-5: Test complex scripts

**Week 4: Testing & Polish**
- Day 1-3: Comprehensive testing
- Day 4: Documentation
- Day 5: Release preparation

### 7.2 Build Configuration

**File:** `CMakeLists.txt` (root)

```cmake
# Add Scarface build option
option(SCARFACE_COMPATIBLE "Build Scarface-compatible compiler" OFF)

if(SCARFACE_COMPATIBLE)
    message(STATUS "Building Scarface-compatible compiler")
    
    add_definitions(
        -DSCARFACE_COMPATIBLE
        -DSCARFACE_FLOAT_F32
        -DSCARFACE_NO_LINEBREAKS
        -DSCARFACE_MAX_OPCODES=81
    )
    
    # Set compiler flags
    if(MSVC)
        add_compile_options(/W4)
    else()
        add_compile_options(-Wall -Wextra)
    endif()
endif()

# Console system library
add_library(torque3d_console
    Engine/source/console/compiler.cpp
    Engine/source/console/codeBlock.cpp
    Engine/source/console/codeInterpreter.cpp
    Engine/source/console/astNodes.cpp
    Engine/source/console/CMDscan.cpp
    # ... other files ...
)

target_include_directories(torque3d_console PUBLIC
    Engine/source
)

if(SCARFACE_COMPATIBLE)
    target_compile_definitions(torque3d_console PUBLIC
        SCARFACE_COMPATIBLE
        SCARFACE_FLOAT_F32
        SCARFACE_NO_LINEBREAKS
    )
endif()
```

### 7.3 Command-Line Compiler Tool

**File:** `Tools/scarfaceCompiler/main.cpp` (NEW)

```cpp
#include <stdio.h>
#include <stdlib.h>
#include "platform/platform.h"
#include "console/console.h"
#include "console/codeBlock.h"
#include "core/stream/fileStream.h"

void printUsage(const char* prog) {
    printf("Scarface TorqueScript Compiler v1.0\n\n");
    printf("Usage: %s [options] <input.cs> [output.cso]\n\n", prog);
    printf("Options:\n");
    printf("  -h, --help       Show this help\n");
    printf("  -v, --verbose    Verbose output\n");
    printf("  -o <file>        Output file\n");
    printf("  --dump           Dump bytecode\n");
    printf("\n");
}

int main(int argc, char** argv) {
    const char* inputFile = NULL;
    const char* outputFile = NULL;
    bool verbose = false;
    bool dump = false;
    
    // Parse arguments
    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "-h") == 0 || 
            strcmp(argv[i], "--help") == 0) {
            printUsage(argv[0]);
            return 0;
        }
        else if (strcmp(argv[i], "-v") == 0) {
            verbose = true;
        }
        else if (strcmp(argv[i], "--dump") == 0) {
            dump = true;
        }
        else if (strcmp(argv[i], "-o") == 0 && i + 1 < argc) {
            outputFile = argv[++i];
        }
        else if (!inputFile) {
            inputFile = argv[i];
        }
        else if (!outputFile) {
            outputFile = argv[i];
        }
    }
    
    if (!inputFile) {
        printf("Error: No input file\n");
        printUsage(argv[0]);
        return 1;
    }
    
    // Generate output name
    char defaultOutput[1024];
    if (!outputFile) {
        strcpy(defaultOutput, inputFile);
        char* ext = strrchr(defaultOutput, '.');
        if (ext && strcmp(ext, ".cs") == 0)
            strcpy(ext, ".cso");
        else
            strcat(defaultOutput, ".cso");
        outputFile = defaultOutput;
    }
    
    if (verbose) {
        printf("Input:  %s\n", inputFile);
        printf("Output: %s\n", outputFile);
    }
    
    // Initialize platform
    Platform::init();
    
    // Read source file
    FileStream inStream;
    if (!inStream.open(inputFile, Torque::FS::File::Read)) {
        printf("Error: Cannot open input file\n");
        return 1;
    }
    
    U32 size = inStream.getStreamSize();
    char* script = new char[size + 1];
    inStream.read(size, script);
    script[size] = '\0';
    inStream.close();
    
    if (verbose)
        printf("Read %d bytes\n", size);
    
    // Compile
    CodeBlock* code = new CodeBlock();
    StringTableEntry name = StringTable->insert(inputFile);
    
    if (!code->compile(outputFile, name, script, true)) {
        printf("Error: Compilation failed\n");
        delete[] script;
        delete code;
        Platform::shutdown();
        return 1;
    }
    
    delete[] script;
    
    if (verbose)
        printf("Success: %d instructions\n", code->codeSize);
    
    if (dump)
        code->dumpInstructions();
    
    printf("Output: %s\n", outputFile);
    
    delete code;
    Platform::shutdown();
    
    return 0;
}
```

**File:** `Tools/scarfaceCompiler/CMakeLists.txt` (NEW)

```cmake
cmake_minimum_required(VERSION 3.15)
project(ScarfaceCompiler)

# Force Scarface mode
set(SCARFACE_COMPATIBLE ON CACHE BOOL "Scarface compatibility" FORCE)
set(SCARFACE_FLOAT_F32 ON CACHE BOOL "Use F32 floats" FORCE)

# Add engine source
add_subdirectory(../../Engine/source torque3d)

# Compiler executable
add_executable(scarfaceCompiler
    main.cpp
)

target_link_libraries(scarfaceCompiler
    torque3d_console
    torque3d_core
    torque3d_platform
)

target_compile_definitions(scarfaceCompiler PRIVATE
    SCARFACE_COMPATIBLE
    SCARFACE_FLOAT_F32
    SCARFACE_NO_LINEBREAKS
)

# Install
install(TARGETS scarfaceCompiler
    RUNTIME DESTINATION bin
)
```

**End of Part 3** - File size: ~48KB

Continue to **Part 4** for:
- Testing & Validation
- Advanced Topics
- Complete Appendices
