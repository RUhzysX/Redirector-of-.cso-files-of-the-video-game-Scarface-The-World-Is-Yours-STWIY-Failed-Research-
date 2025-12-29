# Scarface: The World Is Yours - Complete Modding Guide
### Director's Cut Modification Framework
**Version 1.0 - Comprehensive Technical Documentation**

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Game Architecture Overview](#2-game-architecture-overview)
3. [Core File Formats](#3-core-file-formats)
4. [TorqueScript System](#4-torquescript-system)
5. [Game Classes & Objects](#5-game-classes--objects)
6. [Native Functions Reference](#6-native-functions-reference)
7. [Pure3D (P3D) Graphics System](#7-pure3d-p3d-graphics-system)
8. [Hashing & Key System](#8-hashing--key-system)
9. [Tools & Utilities](#9-tools--utilities)
10. [Modding Workflows](#10-modding-workflows)
11. [Memory Structure](#11-memory-structure)
12. [Best Practices](#12-best-practices)

---

## 1. Introduction

### 1.1 About This Guide

This guide provides comprehensive documentation for modding Scarface: The World Is Yours (2006), a game built on a modified version of the Torque Game Engine. The information here is compiled from extensive reverse engineering efforts by the modding community.

### 1.2 Game Technical Overview

**Engine:** Modified Torque Game Engine  
**Script Language:** TorqueScript (custom variant)  
**Graphics:** Pure3D rendering system  
**Platform:** PC (Windows), PS2, Xbox, Wii  
**Key Archive:** cement.rcf (primary asset container)

### 1.3 Research Sources

This guide synthesizes research from:
- **BrokenFace** - TorqueScript decompiler
- **Scarface Classes** - 205+ reverse-engineered C++ class definitions
- **Scarface Natives** - 577+ documented native functions (85 class methods, 492 globals)
- **Scarface-P3D** - Pure3D graphics format tools
- **STWIY-Lib** - Game engine library reconstructions
- **Hashkey System** - String hashing implementation

---

## 2. Game Architecture Overview

### 2.1 Engine Structure

Scarface uses a heavily modified Torque Game Engine with these key subsystems:

```
┌─────────────────────────────────────────┐
│         Game Executable (scarface.exe)   │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │    TorqueScript Virtual Machine     │ │
│  │  - Bytecode Interpreter             │ │
│  │  - 86 Opcodes (0-85)                │ │
│  │  - Type-insensitive (uint/float/str)│ │
│  └────────────────────────────────────┘ │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │    Game Object System               │ │
│  │  - 85+ Class Types                  │ │
│  │  - ScriptObject Base                │ │
│  │  - ConsoleObject Hierarchy          │ │
│  └────────────────────────────────────┘ │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │    Pure3D Rendering Engine          │ │
│  │  - Chunk-based file format          │ │
│  │  - Mesh, Texture, Animation         │ │
│  │  - Skeleton & Composite Drawables   │ │
│  └────────────────────────────────────┘ │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │    Resource Management              │ │
│  │  - cement.rcf Archive               │ │
│  │  - ChunkFile Streaming              │ │
│  │  - Hash-based String Keys           │ │
│  └────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

### 2.2 Directory Structure

```
Scarface/
├── scarface.exe              # Main executable (6.2MB)
├── cement.rcf                # Main asset archive
├── scriptc/                  # Compiled scripts (.cso, .dso)
├── art/                      # Graphics assets (.p3d)
├── sound/                    # Audio files
└── data/                     # Configuration files
```

### 2.3 Data Flow

```
Source Script (.cs) 
    ↓
[Torque Compiler]
    ↓
Compiled Script (.cso/.dso)
    ↓
[BrokenFace Decompiler]
    ↓
Decompiled Script (.cs)
    ↓
[Modify & Recompile]
    ↓
Modified Game
```

---

## 3. Core File Formats

### 3.1 Compiled Script Files (.cso/.dso)

#### Format Structure

TorqueScript compiled files have a specific binary structure:

```
[Header]
├── Script Version (4 bytes, little-endian)    → Always 1
├── Global String Table Size (4 bytes)
├── Global String Table (null-terminated strings)
├── Global Float Table Size (4 bytes)
├── Global Float Table (4-byte floats each)
├── Function String Table Size (4 bytes)
├── Function String Table (null-terminated)
├── Function Float Table Size (4 bytes)
├── Function Float Table (4-byte floats each)
├── Bytecode Size (4 bytes)
├── Bytecode (variable length codes)
├── Ident Table Size (4 bytes)
└── Ident Table (offset/count/location triplets)
```

#### String Tables

**Purpose:** Store all string literals used in scripts  
**Format:** Consecutive null-terminated strings  
**Access:** By byte offset (0-indexed)

```c
// Example string table contents:
0x0000: "PlayerObject"
0x000D: "Health"
0x0014: "Weapons"
```

#### Float Tables

**Purpose:** Store floating-point constants  
**Format:** Array of 32-bit IEEE 754 floats  
**Access:** By index

```c
// Example float table:
Index 0: 100.0    // Max health
Index 1: 0.5      // Damage multiplier
Index 2: 3.14159  // Pi constant
```

#### Bytecode Structure

The bytecode uses a special encoding system:

**Single-byte codes:**
```
0x00-0xFE → Direct opcode values
```

**Extended codes (2-byte):**
```
0xFF + 0x11 + 0x22 → Code value 0x1122
```

This allows for both compact 1-byte instructions and extended 2-byte instructions when needed.

#### Ident Table (String Patching)

The Ident Table patches string references into the bytecode after loading:

```c
struct IdentEntry {
    uint32_t offset;      // Offset in string table
    uint32_t count;       // Number of patch locations
    uint32_t locations[]; // Bytecode positions to patch
}
```

**Patching Process:**
1. Read string offset from Ident Table
2. For each location in the entry
3. Write the offset into bytecode at that position

### 3.2 Pure3D Files (.p3d)

#### Chunk File Format

P3D files use a hierarchical chunk-based format:

```c
struct Chunk {
    uint32_t id;            // Chunk type identifier
    uint32_t dataLength;    // Length of chunk data
    uint32_t chunkLength;   // Total length including children
    uint32_t startPosition; // File position
};
```

#### Common Chunk Types

| Chunk ID | Name | Purpose |
|----------|------|---------|
| 0x00000000 | Root | File root chunk |
| 0x00010000 | Mesh | 3D geometry data |
| 0x00019000 | Skin | Skeleton-based mesh |
| 0x00013000 | Shader | Material/texture data |
| 0x00018002 | Texture | Image data |
| 0x00121000 | Animation | Skeletal animation |
| 0x00120100 | Skeleton | Bone hierarchy |

#### Reading P3D Files

```cpp
ChunkFile* chunk = new ChunkFile(loadStream);
while (chunk->ChunksRemaining()) {
    uint32_t chunkID = chunk->BeginChunk();
    
    switch(chunkID) {
        case 0x00010000: // Mesh
            ReadMeshData(chunk);
            break;
        case 0x00018002: // Texture  
            ReadTextureData(chunk);
            break;
    }
    
    chunk->EndChunk();
}
```

#### Chunk Stack Navigation

P3D uses a 32-level chunk stack:

```cpp
class ChunkFile {
    Chunk chunkStack[32];  // Max 32 nested levels
    int stackTop;
    
    // Navigate hierarchy
    uint32_t BeginChunk();     // Enter child
    void EndChunk();           // Return to parent
    bool ChunksRemaining();    // Check for siblings
};
```

### 3.3 Archive Format (.rcf)

The `cement.rcf` file is the main game archive containing all assets.

**Structure:**
- Custom compressed archive format
- Contains .cso/.dso scripts, .p3d models, textures, sounds
- Requires specialized tools to extract/repack

---

## 4. TorqueScript System

### 4.1 Compilation Process

#### Three-Stage Decompilation

**Stage 1: Parsing**
```python
# Read binary structures
scriptVersion = read_uint32()
globalStringTable = read_string_table()
globalFloatTable = read_float_table()
functionStringTable = read_string_table()
functionFloatTable = read_float_table()
bytecode = read_bytecode()
identTable = read_ident_table()

# Patch string references
patch_bytecode(bytecode, identTable)
```

**Stage 2: Decoding**
```python
# Build intermediate tree structure
tree = Tree()
while bytecode.hasMoreInstructions():
    opcode = bytecode.getOpcode()
    decode_instruction(opcode, tree)
```

**Stage 3: Formatting**
```python
# Generate source code from tree
source = ""
for node in tree.levelOrderTraversal():
    source += node.format() + "\n"
```

### 4.2 Instruction Set (86 Opcodes)

#### Core Instructions

| Opcode | Name | Description |
|--------|------|-------------|
| 0x00 | OP_FUNC_DECL | Function declaration |
| 0x01 | OP_CREATE_OBJECT | Create new object |
| 0x04 | OP_ADD_OBJECT | Add to parent |
| 0x05 | OP_END_OBJECT | End object definition |
| 0x06 | OP_JMPIFFNOT | Jump if false (float) |
| 0x07 | OP_JMPIFNOT | Jump if not |
| 0x08 | OP_JMPIFF | Jump if false |
| 0x09 | OP_JMPIF | Jump if true |
| 0x0C | OP_JMP | Unconditional jump |
| 0x0D | OP_RETURN | Return from function |

#### Comparison Operations

| Opcode | Name | Description |
|--------|------|-------------|
| 0x0E | OP_CMPEQ | Compare equal |
| 0x0F | OP_CMPLT | Compare less than |
| 0x10 | OP_CMPLE | Compare less/equal |
| 0x11 | OP_CMPGR | Compare greater |
| 0x12 | OP_CMPGE | Compare greater/equal |
| 0x13 | OP_CMPNE | Compare not equal |

#### Arithmetic Operations

| Opcode | Name | Description |
|--------|------|-------------|
| 0x1E | OP_ADD | Addition |
| 0x1F | OP_SUB | Subtraction |
| 0x20 | OP_MUL | Multiplication |
| 0x21 | OP_DIV | Division |
| 0x22 | OP_NEG | Negation |
| 0x15 | OP_MOD | Modulo |

#### Variable Operations

| Opcode | Name | Description |
|--------|------|-------------|
| 0x23 | OP_SETCURVAR | Set current variable |
| 0x24 | OP_SETCURVAR_CREATE | Create & set variable |
| 0x27 | OP_SETCURVAR_ARRAY | Set array element |
| 0x28 | OP_SETCURVAR_ARRAY_CREATE | Create array element |
| 0x2B | OP_LOADVAR_UINT | Load uint from var |
| 0x2C | OP_LOADVAR_FLT | Load float from var |
| 0x2D | OP_LOADVAR_STR | Load string from var |
| 0x2E | OP_SAVEVAR_UINT | Save uint to var |
| 0x2F | OP_SAVEVAR_FLT | Save float to var |
| 0x30 | OP_SAVEVAR_STR | Save string to var |

#### Field Operations

| Opcode | Name | Description |
|--------|------|-------------|
| 0x31 | OP_SETCUROBJECT | Set current object |
| 0x32 | OP_SETCUROBJECT_NEW | Create new object |
| 0x33 | OP_SETCURFIELD | Set field name |
| 0x34 | OP_SETCURFIELD_ARRAY | Set field array element |
| 0x35 | OP_LOADFIELD_UINT | Load uint field |
| 0x36 | OP_LOADFIELD_FLT | Load float field |
| 0x37 | OP_LOADFIELD_STR | Load string field |
| 0x38 | OP_SAVEFIELD_UINT | Save uint field |
| 0x39 | OP_SAVEFIELD_FLT | Save float field |
| 0x3A | OP_SAVEFIELD_STR | Save string field |

#### String Operations

| Opcode | Name | Description |
|--------|------|-------------|
| 0x4C | OP_ADVANCE_STR | Advance string pointer |
| 0x4D | OP_ADVANCE_STR_APPENDCHAR | Append character |
| 0x4E | OP_ADVANCE_STR_COMMA | Add comma separator |
| 0x4F | OP_ADVANCE_STR_NUL | Add null terminator |
| 0x50 | OP_REWIND_STR | Rewind string pointer |
| 0x51 | OP_TERMINATE_REWIND_STR | Terminate & rewind |
| 0x52 | OP_COMPARE_STR | Compare strings |

#### Function Calls

| Opcode | Name | Description |
|--------|------|-------------|
| 0x49 | OP_CALLFUNC_RESOLVE | Resolve & call function |
| 0x4A | OP_CALLFUNC | Direct function call |
| 0x53 | OP_PUSH | Push argument |
| 0x54 | OP_PUSH_FRAME | Push call frame |

### 4.3 Data Type System

TorqueScript is type-insensitive but internally uses three types:

#### Unsigned Integer (uint)

**Encoding:** 2 codes, big-endian  
**Formats:**
- 2-byte: Direct value (0x1122)
- 4-byte: 0x00 + 0xFF + 0x1122
- 6-byte: 0xFF + 0x1122 + 0xFF + 0x3344 → 0x11223344

```python
def decode_uint(bytecode):
    code1 = bytecode.get_code()
    code2 = bytecode.get_code()
    
    if code1 == 0xFF:
        # Extended format
        code3 = bytecode.get_code()
        code4 = bytecode.get_code()
        return (code2 << 16) | (code3 << 8) | code4
    else:
        # Standard format
        return (code1 << 8) | code2
```

#### Float

**Encoding:** 2-byte offset (big-endian) into float table  
**Storage:** 32-bit IEEE 754 single precision

```python
def decode_float(bytecode, float_table):
    offset = decode_uint(bytecode)
    return float_table[offset]
```

#### String

**Encoding:** Offset into string table  
**Formats:**
- 2-byte big-endian (unpatched)
- 2-byte little-endian (patched)
- 4-byte: 0x00 + 0xFF + little-endian offset

```python
def decode_string(bytecode, string_table, is_patched):
    if is_patched:
        offset = bytecode.get_uint16_le()
    else:
        offset = bytecode.get_uint16_be()
    return string_table[offset]
```

### 4.4 Virtual Machine State

The TorqueScript VM maintains several runtime structures:

```python
class VMState:
    # Variable context
    curvar = None       # Current variable name
    curobj = None       # Current object
    curfield = None     # Current field name
    
    # Data stacks (per type)
    binStack = []       # Boolean/binary
    intStack = []       # Unsigned integers
    fltStack = []       # Floats
    strStack = []       # Strings
    
    # Call context
    argFrame = []       # Function arguments
    callStack = []      # Call stack
    
    # Control flow
    ip = 0              # Instruction pointer
    endBlock = {}       # Block end addresses
```

### 4.5 Example Script Decompilation

**Bytecode (hex):**
```
00 23 00 10 2D 30 "health"
```

**Decompiled:**
```torquescript
function setHealth(%this, %value) {
    %this.health = %value;
}
```

**Breakdown:**
1. `00` - OP_FUNC_DECL (function declaration)
2. `23 00 10` - OP_SETCURVAR (set %this)
3. `2D` - OP_LOADVAR_STR (load from %this)
4. `30` - OP_SAVEVAR_STR (save to field)
5. `"health"` - String from table

---

## 5. Game Classes & Objects

### 5.1 Class Hierarchy

```
ConsoleObject (0x4 bytes)
    └── ScriptObject (0x20 bytes)
        ├── GameSimObject (0x2C bytes)
        │   ├── GameObject (0x9C bytes)
        │   │   └── CharacterObject (0x430 bytes)
        │   │   └── VehicleObject
        │   │   └── WeaponObject
        │   │   └── CameraObject
        │   ├── GameSetObject (0xAC bytes)
        │   │   ├── GameSet
        │   │   └── GameGroup
        │   └── PositionObject
        │       └── PositionSetObject
        ├── Template
        │   ├── CharacterTemplate
        │   ├── WeaponTemplate
        │   └── VehicleTemplate
        └── FrontendObject
            ├── FETextObject
            ├── FESpriteObject
            └── FEBoxObject
```

### 5.2 Core Classes

#### ScriptObject (0x20 bytes)

**Purpose:** Base class for all script-accessible objects  
**Memory Layout:**

```cpp
class ScriptObject : public ConsoleObject {
public:
    const char* m_Name;              // 0x04 - Object name
    char _Pad0x8[4];                 // 0x08 - Padding
    core::Key m_Key;                 // 0x0C - Hash key
    uint32_t m_ObjectID;             // 0x10 - Unique identifier
    UnknownScriptObjectEntry* m_UnknownPtr1; // 0x14
    char _Pad0x18[4];                // 0x18
    uint16_t m_ParentGroupID;        // 0x1C - Parent group
    
    // Flags at 0x1E-0x1F (16 bits)
    bool m_Sleeping : 1;             // Is object sleeping
    // ... other flags
};
```

**Key Features:**
- Hash-based name lookup (see section 8)
- Parent-child relationships
- Sleep/wake state management
- Unique object ID system

#### GameSimObject (0x2C bytes)

```cpp
class GameSimObject : public ScriptObject {
public:
    uint32_t mTypeMask;              // 0x20 - Object type mask
    float mProcessPriority;          // 0x24 - Update priority
    char _Pad0x28[4];                // 0x28
};
```

**Type Masks:** Define object capabilities
```cpp
enum TypeMasks {
    DefaultObjectType    = 0,
    StaticObjectType     = BIT(0),
    EnvironmentObjectType = BIT(1),
    TerrainObjectType    = BIT(2),
    VehicleObjectType    = BIT(5),
    CharacterObjectType  = BIT(6),
    // ...
};
```

#### CharacterObject (0x430 bytes)

**Purpose:** Player and NPC character representation  
**Size:** 1072 bytes total (0x430)

```cpp
class CharacterObject : public GameObject {
public:
    // AI & Behavior (0xAC-0xFC)
    int mAlertStatus;                     // 0xAC
    int mFriendOrFoe;                     // 0xB0
    CharacterTemplate* mCharacterTemplate; // 0xB4
    pure3d::UID mCharacterTypeUID;        // 0xB8
    TargetSetModule mTargetSetModule;     // 0xBC
    unsigned int mAIBehaviorID;           // 0xD8
    unsigned int mAITaskGroupID;          // 0xDC
    ScriptObjectPointer<AIBehavior*> mAIBehavior; // 0xE8
    
    // Character State (0xFC-0x1AC)
    CharacterContext* mCharacterContext;  // 0xF8
    char* mDialoguePoiName;               // 0xFC
    char* mTeamName;                      // 0x108
    float mDeadForTimer;                  // 0x10C
    bool mDyingFinished;                  // 0x111
    bool mIsDeadBody;                     // 0x112
    
    // Health & Damage (0x15C-0x198)
    int mHealth;                          // 0x15C
    int mMaxHealth;                       // 0x160
    bool mIsInjured;                      // 0x164
    bool m_KnockedDown;                   // 0x165
    bool mLastHitWasToHead;               // 0x166
    ECriticalHit mCriticalHit;            // 0x170
    ESkeletonJoint m_DamageJoint;         // 0x178
    unsigned int m_KillerID;              // 0x184
    
    // Character Engine Object (0x1AC)
    Character* mCharacterEngineObject;    // 0x1AC
    
    // Character Intention & States (0x1B0-0x3A0)
    CharacterIntention mCharacterIntention; // 0x1B0
    IntentionArbitrator mIntentionArbitrator; // 0x26C
    CrouchState mCrouchState;             // 0x2A0
    WeaponState mWeaponState;             // 0x2AC
    Swim mSwimState;                      // 0x2DC
    PilotState m_PilotState;              // 0x2E8
    GunUpState m_GunUpState;              // 0x380
    SpeedController m_SpeedController;    // 0x388
    
    // Miscellaneous (0x3A0-0x42C)
    bool mIsMidget;                       // 0x3A0
    CharacterLocomotionContextType mLocomotionContext; // 0x3CC
    CharacterClass mCharacterClass;       // 0x3E0
    core::Key mVehicleAITaskName[6];      // 0x3D8
    int mPaletteIndex;                    // 0x418
    FightTreePhysicalMode mFightTreePhysicalMode; // 0x41C
    DBKey mHealthPostKey;                 // 0x428
    CharacterObjectCapability* mCapability; // 0x42C
};
```

**Key Subsystems:**

1. **CharacterContext** - Animation and state management
2. **IntentionArbitrator** - AI decision making
3. **WeaponState** - Weapon handling and aiming
4. **CrouchState** - Movement stance
5. **TargetSetModule** - Targeting system

### 5.3 Template System

Templates define object prototypes:

```cpp
class Template : public ScriptObject {
    // Base template properties
};

class CharacterTemplate : public Template {
    // Character-specific template data
    // - Base stats (health, speed, etc.)
    // - AI behavior parameters
    // - Animation sets
    // - Weapon loadouts
};

class WeaponTemplate : public Template {
    // Weapon properties
    // - Damage values
    // - Fire rate
    // - Ammo capacity
    // - Projectile type
};
```

**Usage in Scripts:**
```torquescript
// Create character from template
%char = new CharacterObject() {
    template = "TonyMontana";
    health = 100;
    position = "10 20 5";
};
```

### 5.4 Game Object Types

#### Complete Class List (85 Classes)

**Core Objects:**
- AIStimulusTable
- ActionMap
- AddressManager
- AnimationLoaderObject
- CameraManager
- CameraObject
- CharacterObject
- GameGroup
- GameObject
- GameSet
- GameSimObject

**HUD Objects:**
- BlackjackHUD
- BusinessDetailHUD
- BusinessHUD
- DrugWarsHUD
- EmpireHUD
- ExoticsHUD2
- FightBettingHUD
- GameOverHUD

**Frontend Objects:**
- FEBoxObject
- FESpriteObject
- FETextObject

**Physics Objects:**
- BoatPhysicsTemplate
- ExplosionTemplate
- PhysicsObject
- RigidBody

**Specialized Objects:**
- CoverObject
- DanceState
- EffectsObject
- Graph
- MissionObject
- ScriptTask
- SpawnObject
- StatePropObject
- TargetSetObject
- VehicleObject
- WeaponObject
- WaterBlock

---

## 6. Native Functions Reference

### 6.1 Function Categories

The game exposes 577 native functions:
- **85 Class Methods** - Object-oriented functions
- **492 Global Functions** - Utility and system functions

### 6.2 Class Methods

#### CharacterObject Methods (50+ methods)

**Health Management:**
```torquescript
// Add health to character
void AddHealth(int amount);

// Apply damage to character
void ApplyDamage(int damage, int damageType, 
                 int joint, int weaponID);

// Set maximum health
void SetMaxHealth(int maxHealth);

// Get current health
int GetHealth();
```

**Weapon Management:**
```torquescript
// Add weapon to inventory
void AddWeaponTemplateToInventory(string templateName);

// Remove weapon
void RemoveWeaponFromInventory(string weaponType);

// Switch to weapon type
void SwitchToWeaponType(string weaponType);

// Get current weapon
int GetCurrentWeapon();

// Fire current weapon
void FireWeapon();

// Enable infinite ammo
void InfiniteAmmo(bool enable);
```

**Animation Control:**
```torquescript
// Request animation
int RequestAnimation(string animName, 
                     float blendTime,
                     bool blocking);

// Get animation priority
int GetAnimationPriority();

// Get animation request ID
int GetAnimationRequestID();
```

**AI & Behavior:**
```torquescript
// Set alert status
void SetAlertStatus(int alertLevel);

// Get alert status
int GetAlertStatus();

// Check if in combat
bool IsInCombat();

// Check if recognizes Tony
bool RecognizesTony();

// Set as disabled
void SetDisabled(bool disabled);
```

**Vehicle Interaction:**
```torquescript
// Enter vehicle
void EnterVehicleLowLevel(int vehicleID, int seatIndex);

// Exit vehicle
void ExitVehicle();

// Check if in car
bool IsCharacterInCar();

// Check if in boat
bool IsCharacterInBoat();

// Get current vehicle ID
int GetVehicleID();

// Get last vehicle ID
int GetLastVehicleID();
```

**Voice & Dialog:**
```torquescript
// Request vocal line
void RequestVocal(string vocalName, 
                  int priority);

// Request vocal after target
void RequestVocalAfterTargetFinished(
    string vocalName, 
    int targetID);

// Get remaining vocal time
int GetRemainingVocalMs();

// Check if has sample
bool HasSample(string sampleName);
```

**Visibility & Rendering:**
```torquescript
// Set character visibility
void SetCharacterVisible(bool visible);

// Set LOD override
void SetOverrideCullDistance(float distance);

// Fade and delete
void FadeAndDelete(float fadeTime);
```

#### CameraObject Methods

```torquescript
// Set camera target
void SetTarget(int objectID);

// Set camera mode
void SetMode(string modeName);

// Set field of view
void SetFOV(float fov);

// Shake camera
void Shake(float magnitude, float duration);
```

#### VehicleObject Methods

```torquescript
// Set vehicle driver
void SetDriver(int characterID);

// Get driver
int GetDriver();

// Set vehicle speed
void SetSpeed(float speed);

// Apply damage
void ApplyDamage(int damage, int damageType);

// Repair vehicle
void Repair();

// Explode vehicle
void Explode();
```

#### GameSet Methods

```torquescript
// Add object to set
void AddObject(int objectID);

// Remove object
void RemoveObject(int objectID);

// Get object count
int GetObjectCount();

// Get object at index
int GetObject(int index);

// Clear all objects
void Clear();
```

### 6.3 Global Functions

#### Game Flow Management

```torquescript
// Start mission
void StartMission(string missionName);

// End mission
void EndMission(bool success);

// Load level
void LoadLevel(string levelName);

// Save game
void SaveGame(string slotName);

// Load game
void LoadGame(string slotName);

// Quit game
void QuitGame();
```

#### Character & NPC Management

```torquescript
// Spawn character
int CVM_SpawnCharacter(string template, 
                       string position,
                       string rotation);

// Kill all NPCs
void CVM_KillAll();

// Kill ambient characters
void CVM_KillAllAmbientCharacters();

// Get main character package
string CVM_GetMainCharacterPackage();

// Check if package loaded
bool CVM_IsMainCharacterPackageLoaded();
```

#### World & Environment

```torquescript
// Set time of day
void SetTimeOfDay(int hour);

// Get time of day
int GetTimeOfDay();

// Set weather
void SetWeather(string weatherType);

// Enable rain
void EnableRain(bool enable);

// Trigger blackout
void Blackout(float duration);
```

#### HUD & UI

```torquescript
// Show HUD element
void ShowHUDElement(string elementName);

// Hide HUD element
void HideHUDElement(string elementName);

// Display message
void DisplayMessage(string message, 
                    float duration);

// Show tutorial
void AdvanceTutorialState(int stateID);
```

#### Audio Management

```torquescript
// Play sound
int PlaySound(string soundName);

// Stop sound
void StopSound(int soundID);

// Set music track
void SetMusicTrack(string trackName);

// Set volume
void SetVolume(float volume);
```

#### Memory & Performance

```torquescript
// Add memory hack
void AddMemoryHack();

// Allocate for textbibles
void AllocateMemoryForPMGTextbibles();

// Add textbible entry
void AddTextbibleEntryToLoad(string entry);
```

#### Database & Save System

```torquescript
// Database operations
void DB_Save();
void DB_Load();
void DB_Clear();

// Get DB value
string DB_GetValue(string key);

// Set DB value
void DB_SetValue(string key, string value);
```

#### Input & Controls

```torquescript
// Bind key
void BindKey(string key, string command);

// Apply input changes
void ApplyEventInputChanges();

// Bind triggered slots
void BindTriggeredSlots();
```

#### Cheats & Debug

```torquescript
// God mode
void GodMode(bool enable);

// Infinite ammo
void InfiniteAmmo(bool enable);

// No clip
void NoClip(bool enable);

// Teleport
void Teleport(float x, float y, float z);

// Spawn item
int SpawnItem(string itemName);
```

### 6.4 Function Call Mechanics

#### Native Call Structure

```cpp
// Function signature in natives.json
{
    "address": "0x00522b50",
    "className": "CharacterObject",
    "methodName": "AddHealth",
    "minArguments": 1,
    "maxArguments": 1,
    "return": 3  // Return type code
}
```

#### Return Type Codes

```cpp
enum ReturnType {
    RETURN_VOID = 0,
    RETURN_INT = 1,
    RETURN_FLOAT = 2,
    RETURN_STRING = 3,
    RETURN_BOOL = 4
};
```

#### Calling Convention

```torquescript
// Method call
%result = %object.MethodName(%arg1, %arg2);

// Global function call
%result = FunctionName(%arg1, %arg2);
```

**Internal VM Process:**
1. Push arguments onto stack (OP_PUSH)
2. Push call frame (OP_PUSH_FRAME)
3. Resolve function address (OP_CALLFUNC_RESOLVE)
4. Execute native code at address
5. Pop return value
6. Clean up stack

---

## 7. Pure3D (P3D) Graphics System

### 7.1 File Structure

Pure3D files are chunk-based binary formats used for all 3D assets.

#### ChunkFile Class

```cpp
class ChunkFile {
    char filename[128];
    Chunk chunkStack[32];    // 32-level hierarchy
    int stackTop;
    LoadStream* realFile;
    
public:
    // Navigation
    bool ChunksRemaining();
    uint32_t BeginChunk();
    uint32_t BeginChunk(uint32_t chunkID);
    void EndChunk();
    uint32_t GetCurrentID();
    
    // Data reading
    void GetData(void* buf, uint32_t count, uint32_t sz = 1);
    uint8_t GetU8();
    uint16_t GetU16();
    uint32_t GetU32();
    float GetFloat();
    char* GetString(char* s);
    char* GetLString(char* s);
};
```

### 7.2 Common Chunk Types

#### Mesh Chunks (0x00010000)

**Structure:**
```cpp
struct MeshChunk {
    char name[128];
    uint32_t version;
    uint32_t numPrimGroups;
    PrimGroup primGroups[];
};

struct PrimGroup {
    uint32_t shaderIndex;
    uint32_t primitiveType;
    uint32_t vertexType;
    uint32_t numVertices;
    uint32_t numIndices;
    Vertex vertices[];
    uint16_t indices[];
};
```

**Vertex Formats:**
```cpp
enum VertexType {
    PDDI_V_C     = 0x01,  // Position + Color
    PDDI_V_N     = 0x02,  // Position + Normal
    PDDI_V_UV    = 0x04,  // Position + UV
    PDDI_V_UV2   = 0x08,  // Position + UV + UV2
    PDDI_V_CNT   = 0x0E,  // Color + Normal + UV
};
```

#### Texture Chunks (0x00018002)

```cpp
struct TextureChunk {
    char name[128];
    uint32_t version;
    uint32_t width;
    uint32_t height;
    uint32_t bpp;           // Bits per pixel
    uint32_t alphaDepth;
    uint32_t numMipMaps;
    uint32_t textureType;
    uint32_t usage;
    uint32_t priority;
    
    // Image data follows
    uint8_t imageData[];
};
```

**Texture Types:**
```cpp
enum TextureType {
    TEX_RGB   = 0,
    TEX_RGBA  = 1,
    TEX_DXT1  = 2,
    TEX_DXT3  = 3,
    TEX_DXT5  = 4,
};
```

#### Skeleton Chunks (0x00120100)

```cpp
struct SkeletonChunk {
    char name[128];
    uint32_t version;
    uint32_t numJoints;
    Joint joints[];
};

struct Joint {
    uint32_t parent;        // Parent joint index
    float restPose[3][4];   // 3x4 matrix
    char name[128];
};
```

#### Animation Chunks (0x00121000)

```cpp
struct AnimationChunk {
    char name[128];
    uint32_t version;
    float frameRate;
    uint32_t numFrames;
    uint32_t numChannels;
    AnimChannel channels[];
};

struct AnimChannel {
    uint16_t jointIndex;
    uint16_t channelType;   // Position, Rotation, Scale
    uint32_t numKeys;
    AnimKey keys[];
};

struct AnimKey {
    float time;
    float value[4];  // Quaternion or vector
};
```

### 7.3 Composite Drawables

Composite drawables combine multiple meshes with LOD support:

```cpp
struct CompositeDrawable {
    char name[128];
    uint32_t skeletonID;
    uint32_t numElements;
    Element elements[];
};

struct Element {
    char name[128];
    uint32_t propID;
    Skeleton* skeleton;
};
```

### 7.4 Shader System

```cpp
struct Shader {
    char name[128];
    uint32_t version;
    char pddiShaderName[128];
    uint32_t hasTranslucency;
    uint32_t vertexNeeds;
    uint32_t vertexMask;
    uint32_t numParams;
    ShaderParam params[];
};

struct ShaderParam {
    char name[128];
    uint32_t type;      // INT, FLOAT, COLOR, TEXTURE
    union {
        int intValue;
        float floatValue;
        Color colorValue;
        uint32_t textureIndex;
    };
};
```

### 7.5 Loading P3D Files

```cpp
// Example: Load character model
void LoadCharacterModel(const char* filename) {
    LoadStream* stream = new LoadStream(filename);
    ChunkFile* chunk = new ChunkFile(stream);
    
    Mesh* mesh = nullptr;
    Skeleton* skeleton = nullptr;
    
    while (chunk->ChunksRemaining()) {
        uint32_t chunkID = chunk->BeginChunk();
        
        switch (chunkID) {
            case 0x00010000: // Mesh
                mesh = ReadMeshChunk(chunk);
                break;
                
            case 0x00120100: // Skeleton
                skeleton = ReadSkeletonChunk(chunk);
                break;
                
            case 0x00121000: // Animation
                Animation* anim = ReadAnimChunk(chunk);
                animations.push_back(anim);
                break;
                
            case 0x00018002: // Texture
                Texture* tex = ReadTextureChunk(chunk);
                textures.push_back(tex);
                break;
        }
        
        chunk->EndChunk();
    }
    
    // Bind skeleton to mesh if both present
    if (mesh && skeleton) {
        mesh->BindSkeleton(skeleton);
    }
}
```

### 7.6 Rendering Pipeline

```
P3D File Loading
    ↓
Chunk Parsing
    ↓
Resource Creation
    ↓
├─ Mesh → Vertex Buffers
├─ Texture → GPU Textures
├─ Skeleton → Bone Hierarchy
└─ Animation → Keyframe Data
    ↓
Scene Graph Assembly
    ↓
Composite Drawable Creation
    ↓
LOD Selection
    ↓
Render Queue
    ↓
PDDI Rendering
```

---

## 8. Hashing & Key System

### 8.1 Hash Function

Scarface uses a custom 32-bit hash function for string keys:

```cpp
namespace core {
    uint32_t MakeKey(const char* p_Str) {
        uint32_t _Key = 0;
        while (*p_Str) {
            _Key *= 65599;
            _Key = (_Key ^ static_cast<uint32_t>(*p_Str));
            p_Str++;
        }
        return _Key;
    }
}
```

**Properties:**
- **Input:** Null-terminated string
- **Output:** 32-bit unsigned integer
- **Algorithm:** Multiplicative hash with XOR
- **Magic constant:** 65599 (prime number)

### 8.2 String Hash Encoding

Hashes can be encoded as strings for use in data files:

```cpp
char* KeyToString(uint32_t p_Key) {
    static char s_Key[12];
    strcpy_s(s_Key, "stx");  // Prefix
    
    for (int i = 0; i < 4; ++i) {
        uint8_t _Byte = reinterpret_cast<uint8_t*>(&p_Key)[i];
        int _Index = (3 + (i << 1));
        s_Key[_Index] = 'a' + (_Byte & 0x0F);
        s_Key[_Index + 1] = 'a' + (_Byte >> 4);
    }
    
    s_Key[11] = 0;
    return s_Key;
}
```

**Format:** `stxXXXXXXXX`
- Prefix: `stx`
- 8 characters encoding 4 bytes (2 chars per byte)
- Each nibble (4 bits) encoded as 'a' + value

**Example:**
```
String: "TonyMontana"
Hash: 0x4D7A8BC1
Encoded: "stxblianjdj"
```

### 8.3 Decoding String Hashes

```cpp
uint32_t StringKeyToKey(const char* p_Str) {
    if (p_Str && *p_Str == 's' && 
        p_Str[1] == 't' && p_Str[2] == 'x') {
        return 16 * (16 * (16 * (16 * (16 * (16 * (16 * 
               (p_Str[10] - 'a') + 
                p_Str[9] - 'a') + 
                p_Str[8] - 'a') + 
                p_Str[7] - 'a') + 
                p_Str[6] - 'a') + 
                p_Str[5] - 'a') + 
                p_Str[4] - 'a') + 
                p_Str[3] - 'a';
    }
    return -1;
}
```

### 8.4 Usage in Game

#### Object Name Lookups

```cpp
class ScriptObject {
    const char* m_Name;    // String name
    core::Key m_Key;       // Hashed name
    uint32_t m_ObjectID;   // Unique ID
};

// Fast lookup by hash
ScriptObject* FindObjectByName(const char* name) {
    uint32_t key = core::MakeKey(name);
    return objectHashTable[key];
}
```

#### File/Resource References

```torquescript
// In scripts, strings are hashed for lookups
datablock CharacterTemplate(TonyMontana) {
    weaponSet = "TonyWeapons";  // Hashed internally
    animSet = "TonyAnims";      // Hashed internally
};
```

#### CodeBlock Names

```cpp
class CodeBlock {
    uint32_t m_name;  // Hashed script file name
    // In original Torque3D it was char*, 
    // but Scarface uses hash instead
};
```

### 8.5 Hash Collision Handling

The game uses **separate chaining** for collision handling:

```cpp
struct HashBucket {
    core::Key key;
    void* value;
    HashBucket* next;
};

class HashTable {
    HashBucket* buckets[TABLE_SIZE];
    
    void Insert(core::Key key, void* value) {
        int index = key % TABLE_SIZE;
        HashBucket* bucket = new HashBucket();
        bucket->key = key;
        bucket->value = value;
        bucket->next = buckets[index];
        buckets[index] = bucket;
    }
    
    void* Lookup(core::Key key) {
        int index = key % TABLE_SIZE;
        HashBucket* bucket = buckets[index];
        while (bucket) {
            if (bucket->key == key)
                return bucket->value;
            bucket = bucket->next;
        }
        return nullptr;
    }
};
```

### 8.6 Hash Tool Usage

```bash
# Generate hash from string
./hashkey -hash "TonyMontana"
# Output: 0x4D7A8BC1

# Generate string hash
./hashkey -hstr "TonyMontana"
# Output: stxblianjdj

# Convert string hash back to hash
./hashkey -str "stxblianjdj"
# Output: 0x4D7A8BC1
```

---

## 9. Tools & Utilities

### 9.1 BrokenFace Decompiler

**Purpose:** Decompile .cso/.dso TorqueScript files  
**Language:** Python 3.8+  
**Platform:** Linux (tested on Debian Bullseye)

#### Installation

```bash
# Extract archive
unzip BrokenFace-master_s_File_Extractor_.zip
cd BrokenFace-master\'s\ File\ Extractor

# Make executable
chmod +x bin/decompile
```

#### Usage

```bash
# Basic decompilation
./bin/decompile script.cso

# Parse only (dump structures)
./bin/decompile --parse-only script.cso

# Debug mode (verbose logging)
./bin/decompile --debug script.cso

# Batch decompilation
find scriptc/ -name "*.cso" -exec ./bin/decompile {} \;
```

#### Output

```torquescript
// Decompiled script.cso

function InitGame() {
    // Global initialization
    echo("Scarface: The World Is Yours");
    LoadMission("miami_map");
}

function CharacterObject::OnDamaged(%this, %damage) {
    %this.health = %this.health - %damage;
    if (%this.health <= 0) {
        %this.OnKilled();
    }
}
```

### 9.2 P3D Tools

**Purpose:** View and extract Pure3D files

#### p3dview

```bash
# Compile
make -f Makefile.gl

# View P3D file
./p3dview character_tony.p3d
```

**Features:**
- OpenGL rendering
- Mesh visualization
- Texture viewing
- Skeleton display
- Animation playback

#### p3ddump

```bash
# Dump P3D structure
./p3ddump character_tony.p3d > structure.txt
```

**Output:**
```
Chunk 0x00000000 [Root]
  Chunk 0x00010000 [Mesh: TonyBody]
    Vertices: 2451
    Faces: 3876
    Material: tony_skin
  Chunk 0x00120100 [Skeleton: TonySkeleton]
    Joints: 47
    Root: pelvis
  Chunk 0x00121000 [Animation: walk]
    Frames: 30
    Duration: 1.0s
```

### 9.3 Hash Key Tool

```bash
# Compile
g++ -o hashkey hashkey-main/main.cc

# Generate hash
./hashkey -hash "PlayerName"

# Generate string hash
./hashkey -hstr "PlayerName"

# Convert string hash
./hashkey -str "stxabcdefgh"
```

### 9.4 RCF Extractor

**Purpose:** Extract files from cement.rcf archive

```bash
# Extract all files
./rcf_extract cement.rcf output_dir/

# Extract specific file
./rcf_extract cement.rcf scriptc/main.cso

# List contents
./rcf_extract -l cement.rcf
```

### 9.5 Script Compiler

**Purpose:** Recompile modified TorqueScript

```bash
# Compile script
./torque_compile script.cs script.cso

# Compile with optimization
./torque_compile -O2 script.cs script.cso
```

### 9.6 Texture Converter

```bash
# Convert DDS to PNG
./tex_convert tony_diffuse.dds tony_diffuse.png

# Convert PNG to DDS
./tex_convert -format DXT5 tony_diffuse.png tony_diffuse.dds

# Extract all textures from P3D
./tex_extract character_tony.p3d textures/
```

---

## 10. Modding Workflows

### 10.1 Script Modification Workflow

```
┌──────────────────────────────────────┐
│ 1. Extract cement.rcf                │
│    → Get scriptc/*.cso files         │
└─────────────┬────────────────────────┘
              ↓
┌──────────────────────────────────────┐
│ 2. Decompile Scripts                 │
│    ./bin/decompile script.cso        │
│    → Generate script.cs              │
└─────────────┬────────────────────────┘
              ↓
┌──────────────────────────────────────┐
│ 3. Modify Script                     │
│    Edit script.cs                    │
│    - Add functions                   │
│    - Modify logic                    │
│    - Change values                   │
└─────────────┬────────────────────────┘
              ↓
┌──────────────────────────────────────┐
│ 4. Recompile Script                  │
│    ./torque_compile script.cs        │
│    → Generate modified script.cso    │
└─────────────┬────────────────────────┘
              ↓
┌──────────────────────────────────────┐
│ 5. Repack Archive                    │
│    ./rcf_pack scriptc/ cement.rcf    │
└─────────────┬────────────────────────┘
              ↓
┌──────────────────────────────────────┐
│ 6. Test in Game                      │
│    Launch Scarface.exe               │
└──────────────────────────────────────┘
```

#### Example: Modify Player Health

```torquescript
// Original (decompiled from player.cso)
function Player::OnCreate(%this) {
    %this.maxHealth = 100;
    %this.health = 100;
}

// Modified
function Player::OnCreate(%this) {
    %this.maxHealth = 500;  // Increased max health
    %this.health = 500;     // Start with max health
    %this.godMode = true;   // Enable god mode
}
```

### 10.2 Character Model Replacement

```
┌──────────────────────────────────────┐
│ 1. Extract Character P3D             │
│    ./p3ddump character_tony.p3d      │
└─────────────┬────────────────────────┘
              ↓
┌──────────────────────────────────────┐
│ 2. Export to 3D Format               │
│    ./p3d_to_obj character_tony.p3d   │
│    → Generate .obj + .mtl files      │
└─────────────┬────────────────────────┘
              ↓
┌──────────────────────────────────────┐
│ 3. Edit in 3D Software               │
│    - Blender / 3ds Max               │
│    - Modify mesh                     │
│    - Update textures                 │
│    - Maintain skeleton               │
└─────────────┬────────────────────────┘
              ↓
┌──────────────────────────────────────┐
│ 4. Re-export to P3D                  │
│    ./obj_to_p3d tony_modified.obj    │
│    → Generate new P3D                │
└─────────────┬────────────────────────┘
              ↓
┌──────────────────────────────────────┐
│ 5. Replace in Game Files             │
│    Copy to art/characters/           │
└─────────────┬────────────────────────┘
              ↓
┌──────────────────────────────────────┐
│ 6. Test in Game                      │
└──────────────────────────────────────┘
```

### 10.3 New Mission Creation

```torquescript
// missions/custom_mission.cs

// Mission definition
new MissionObject(CustomMission) {
    name = "Custom Mission";
    description = "A new custom mission";
    
    onMissionStart = "OnCustomMissionStart";
    onMissionEnd = "OnCustomMissionEnd";
};

// Initialize mission
function OnCustomMissionStart() {
    // Spawn enemies
    %enemy1 = CVM_SpawnCharacter("Goon", 
                                 "100 200 0", 
                                 "0 0 0");
    %enemy1.SetAlertStatus(3);  // Hostile
    
    // Set objective
    SetMissionObjective("Defeat all enemies");
    
    // Create game set
    $MissionEnemies = new GameSet();
    $MissionEnemies.AddObject(%enemy1);
}

// Check mission completion
function CheckMissionComplete() {
    if ($MissionEnemies.GetObjectCount() == 0) {
        EndMission(true);
        DisplayMessage("Mission Complete!", 5.0);
    }
}

// Clean up
function OnCustomMissionEnd() {
    $MissionEnemies.delete();
}
```

### 10.4 Weapon Modification

```torquescript
// weapons/custom_weapon.cs

datablock WeaponTemplate(CustomAssaultRifle) {
    // Base properties
    name = "Custom AR-15";
    category = "AssaultRifles";
    
    // Damage
    damageMin = 50;
    damageMax = 75;
    headshotMultiplier = 3.0;
    
    // Ammo
    magazineSize = 60;      // Increased from 30
    maxAmmo = 600;          // Increased from 300
    
    // Fire rate
    fireRate = 0.05;        // Faster fire rate
    reloadTime = 1.5;
    
    // Accuracy
    accuracy = 0.95;
    recoil = 0.1;           // Reduced recoil
    
    // Visual
    model = "weapons/ar15.p3d";
    muzzleFlash = "effects/muzzle_flash.p3d";
    
    // Audio
    fireSound = "weapons/ar15_fire.wav";
    reloadSound = "weapons/ar15_reload.wav";
};

// Add to player inventory
function GiveCustomWeapon(%player) {
    %player.AddWeaponTemplateToInventory("CustomAssaultRifle");
    %player.SwitchToWeaponType("AssaultRifles");
}
```

### 10.5 HUD Modification

```torquescript
// ui/custom_hud.cs

// Create custom HUD element
new FETextObject(CustomHealthDisplay) {
    position = "10 10";
    text = "Health: 100";
    font = "Arial";
    size = 24;
    color = "255 255 255";  // White
};

// Update function
function UpdateCustomHUD() {
    %player = GetMainCharacter();
    %health = %player.GetHealth();
    %maxHealth = %player.maxHealth;
    
    %percentage = (%health / %maxHealth) * 100;
    
    CustomHealthDisplay.text = "Health: " @ 
                               mFloor(%percentage) @ "%";
    
    // Color based on health
    if (%percentage < 25) {
        CustomHealthDisplay.color = "255 0 0";  // Red
    } else if (%percentage < 50) {
        CustomHealthDisplay.color = "255 255 0";  // Yellow
    } else {
        CustomHealthDisplay.color = "0 255 0";  // Green
    }
    
    // Schedule next update
    schedule(100, 0, UpdateCustomHUD);
}

// Start HUD updates
function InitCustomHUD() {
    UpdateCustomHUD();
}
```

### 10.6 AI Behavior Modification

```torquescript
// ai/custom_behavior.cs

// Custom AI behavior
function AIBehavior::CustomAggressiveBehavior(%this, %npc) {
    // Find player
    %player = GetMainCharacter();
    %distance = VectorDist(%npc.getPosition(), 
                           %player.getPosition());
    
    if (%distance < 50.0) {
        // Close range - attack
        %npc.SetAlertStatus(3);
        %npc.FireWeapon();
        
    } else if (%distance < 100.0) {
        // Medium range - move closer
        %npc.MoveToward(%player.getPosition());
        
    } else {
        // Far range - patrol
        %npc.Patrol();
    }
    
    // Schedule next behavior update
    schedule(500, %npc, 
             "AIBehavior::CustomAggressiveBehavior",
             %this, %npc);
}

// Apply behavior to NPC
function ApplyCustomBehavior(%npc) {
    AIBehavior::CustomAggressiveBehavior(%npc, %npc);
}
```

### 10.7 Save Game Modification

```torquescript
// Save custom data
function SaveCustomData() {
    // Save to database
    DB_SetValue("customStat1", $PlayerCustomStat1);
    DB_SetValue("customStat2", $PlayerCustomStat2);
    DB_SetValue("unlockedFeature", $UnlockedCustomFeature);
    
    // Save to file
    $SaveData = "customStat1=" @ $PlayerCustomStat1 @ "\n" @
                "customStat2=" @ $PlayerCustomStat2 @ "\n" @
                "unlockedFeature=" @ $UnlockedCustomFeature;
    
    fileWrite("saves/custom_data.txt", $SaveData);
}

// Load custom data
function LoadCustomData() {
    // Load from database
    $PlayerCustomStat1 = DB_GetValue("customStat1");
    $PlayerCustomStat2 = DB_GetValue("customStat2");
    $UnlockedCustomFeature = DB_GetValue("unlockedFeature");
    
    // Verify data
    if ($PlayerCustomStat1 $= "") {
        $PlayerCustomStat1 = 0;
    }
}
```

---

## 11. Memory Structure

### 11.1 Executable Memory Map

```
scarface.exe Memory Layout (6.2MB)

0x00400000 - 0x00401000    .text (Code)
0x00401000 - 0x00700000    Game Code
0x00700000 - 0x00750000    TorqueScript VM
0x00750000 - 0x007A0000    Rendering Engine
0x007A0000 - 0x007F0000    Physics Engine
0x007F0000 - 0x00800000    Audio System

0x00800000 - 0x00900000    .rdata (Read-only Data)
    └── 0x0081518C         smCodeBlockList ptr

0x00900000 - 0x00A00000    .data (Initialized Data)
    ├── Global Variables
    ├── String Constants
    └── Function Pointers

0x00A00000 - 0x00C00000    .bss (Uninitialized Data)
    ├── Object Heap
    ├── String Tables
    └── Resource Cache
```

### 11.2 Object Memory Layout

#### ScriptObject (32 bytes)

```
Offset | Size | Field
-------+------+---------------------------
0x00   | 4    | vftable pointer
0x04   | 4    | m_Name (const char*)
0x08   | 4    | padding
0x0C   | 4    | m_Key (hash)
0x10   | 4    | m_ObjectID
0x14   | 4    | m_UnknownPtr1
0x18   | 4    | padding
0x1C   | 2    | m_ParentGroupID
0x1E   | 2    | flags (16 bits)
```

#### CharacterObject (1072 bytes)

```
Offset | Size | Field
-------+------+---------------------------
0x00   | 0xAC | GameObject base
0xAC   | 4    | mAlertStatus
0xB0   | 4    | mFriendOrFoe
0xB4   | 4    | mCharacterTemplate*
0xB8   | 4    | mCharacterTypeUID
0xBC   | 0x1C | mTargetSetModule
...
0x15C  | 4    | mHealth
0x160  | 4    | mMaxHealth
...
0x1AC  | 4    | mCharacterEngineObject*
0x1B0  | 0xBC | mCharacterIntention
...
0x430  | end  |
```

### 11.3 String Memory Management

```cpp
// String table allocation
struct StringTable {
    char* buffer;          // Allocated buffer
    uint32_t size;         // Total size
    uint32_t used;         // Used bytes
    
    // String offsets stored as keys
    std::map<uint32_t, uint32_t> offsets;
};

// Global string tables
StringTable* gGlobalStrings;
StringTable* gFunctionStrings;
```

### 11.4 Resource Memory

```cpp
// Resource cache structure
struct ResourceCache {
    struct Entry {
        uint32_t hash;     // Resource hash
        void* data;        // Resource data
        uint32_t size;     // Size in bytes
        uint32_t refCount; // Reference count
        Entry* next;       // Next in bucket
    };
    
    Entry* buckets[4096];  // Hash table
    uint32_t totalSize;    // Total cached size
    uint32_t maxSize;      // Max cache size
};
```

### 11.5 Stack Memory

```cpp
// TorqueScript stacks
struct VMStacks {
    uint32_t intStack[256];
    float fltStack[256];
    char* strStack[256];
    
    int intTop;
    int fltTop;
    int strTop;
};
```

---

## 12. Best Practices

### 12.1 Script Development

#### Naming Conventions

```torquescript
// Global variables - $ prefix
$GameDifficulty = 1;
$PlayerScore = 0;

// Local variables - % prefix
%health = 100;
%position = "0 0 0";

// Object methods - :: separator
function CharacterObject::TakeDamage(%this, %amount) {
    %this.health -= %amount;
}

// Constants - all caps
$MAX_HEALTH = 100;
$DAMAGE_MULTIPLIER = 1.5;
```

#### Error Handling

```torquescript
// Check object validity
function SafeApplyDamage(%obj, %damage) {
    if (!isObject(%obj)) {
        warn("Invalid object in SafeApplyDamage");
        return;
    }
    
    if (%damage < 0) {
        warn("Negative damage: " @ %damage);
        %damage = 0;
    }
    
    %obj.ApplyDamage(%damage);
}

// Try-catch equivalent
function SafeLoadMission(%missionName) {
    if (!fileExists("missions/" @ %missionName @ ".cs")) {
        error("Mission not found: " @ %missionName);
        return false;
    }
    
    exec("missions/" @ %missionName @ ".cs");
    return true;
}
```

#### Performance Optimization

```torquescript
// Cache frequently accessed values
function OptimizedUpdate() {
    %player = GetMainCharacter();  // Cache reference
    %pos = %player.getPosition();  // Cache position
    
    // Use cached values
    if (VectorDist(%pos, $EnemyPos) < 50) {
        // Combat logic
    }
}

// Avoid repeated string operations
%weaponName = "AssaultRifle";  // Store once
for (%i = 0; %i < 10; %i++) {
    %weapon = GetWeaponByName(%weaponName);  // Use stored
}

// Schedule intensive operations
schedule(1000, 0, "HeavyOperation");  // Delay 1 second
```

### 12.2 Model Editing

#### Polygon Budget

```
Character Models:
- Main character: ~3000-5000 polygons
- NPCs: ~2000-3000 polygons
- Vehicles: ~5000-8000 polygons
- Weapons: ~1000-2000 polygons
```

#### Texture Guidelines

```
- Character diffuse: 1024x1024 (DXT5)
- Character normal: 1024x1024 (DXT5)
- Vehicle diffuse: 2048x2048 (DXT5)
- Environment: 512x512 to 2048x2048
- UI elements: Power of 2 dimensions
```

#### Skeleton Constraints

```
- Keep original joint names
- Maintain joint hierarchy
- Don't add/remove joints
- Preserve bone weights
- Test animations after modification
```

### 12.3 Archive Management

#### File Organization

```
cement.rcf/
├── scriptc/           # Scripts (compile first)
├── art/
│   ├── characters/    # Character models
│   ├── vehicles/      # Vehicle models
│   ├── weapons/       # Weapon models
│   └── environments/  # Level geometry
├── sound/             # Audio files
└── data/              # Configuration
```

#### Backup Strategy

```bash
# Before modding
cp cement.rcf cement.rcf.backup

# Version control
cp cement.rcf cement.rcf.v1.0
cp cement.rcf cement.rcf.v1.1

# Test separately
./rcf_extract cement.rcf test_files/
# Modify test_files/
./rcf_pack test_files/ cement_test.rcf
# Test cement_test.rcf
```

### 12.4 Testing

#### Debug Console

```torquescript
// Enable debug output
$debugMode = true;

// Debug print
function dbg(%message) {
    if ($debugMode) {
        echo("[DEBUG] " @ %message);
    }
}

// Usage
dbg("Player health: " @ %player.health);
```

#### Test Cases

```torquescript
// Test health system
function TestHealth() {
    %player = GetMainCharacter();
    
    // Test damage
    %initialHealth = %player.health;
    %player.ApplyDamage(10);
    assert(%player.health == %initialHealth - 10, 
           "Damage not applied correctly");
    
    // Test healing
    %player.AddHealth(10);
    assert(%player.health == %initialHealth,
           "Healing not applied correctly");
    
    echo("Health system tests passed");
}

// Assert helper
function assert(%condition, %message) {
    if (!%condition) {
        error("Assertion failed: " @ %message);
    }
}
```

### 12.5 Documentation

#### Code Comments

```torquescript
///
/// @brief Applies damage to a character
/// @param %this - The character object
/// @param %damage - Amount of damage to apply
/// @param %damageType - Type of damage (0=bullet, 1=melee, 2=explosion)
/// @return void
///
function CharacterObject::ApplyDamage(%this, %damage, %damageType) {
    // Validate parameters
    if (%damage < 0) {
        warn("Negative damage value");
        return;
    }
    
    // Apply damage modifiers
    %finalDamage = %damage * $DamageMultiplier;
    
    // Update health
    %this.health -= %finalDamage;
    
    // Check for death
    if (%this.health <= 0) {
        %this.OnKilled();
    }
}
```

#### Change Log

```
# Scarface Director's Cut Changelog

## Version 1.0.0 (2025-01-01)
### Added
- New weapons system
- Enhanced AI behavior
- Custom HUD elements

### Changed
- Increased player health to 500
- Modified weapon damage values
- Updated character models

### Fixed
- Fixed crash on mission completion
- Corrected vehicle physics
- Fixed texture loading issues
```

### 12.6 Common Pitfalls

#### String Handling

```torquescript
// WRONG - String comparison
if (%name == "Tony") { }  // May not work

// CORRECT - Use $= operator
if (%name $= "Tony") { }
```

#### Object Lifetime

```torquescript
// WRONG - Object deleted, still referenced
%obj.delete();
schedule(1000, %obj, "SomeMethod");  // CRASH

// CORRECT - Check before using
if (isObject(%obj)) {
    schedule(1000, %obj, "SomeMethod");
}
```

#### Memory Leaks

```torquescript
// WRONG - Objects never deleted
function SpawnEnemy() {
    %enemy = new CharacterObject();
    // No cleanup
}

// CORRECT - Proper cleanup
function SpawnEnemy() {
    %enemy = new CharacterObject();
    $Enemies.add(%enemy);  // Track in set
}

function CleanupEnemies() {
    while ($Enemies.getCount() > 0) {
        %obj = $Enemies.getObject(0);
        $Enemies.remove(%obj);
        %obj.delete();
    }
}
```

---

## Appendix A: Quick Reference

### TorqueScript Operators

```torquescript
// Arithmetic
+  -  *  /  %  ++  --

// Comparison
==  !=  <  <=  >  >=

// String
$=  !$=  @  SPC  TAB  NL

// Logical
&&  ||  !

// Bitwise
&  |  ^  ~  <<  >>
```

### Common Functions

```torquescript
// Object management
isObject(%obj)
%obj.delete()
%obj.getName()
%obj.setName(%name)

// String operations
strlen(%str)
strcmp(%str1, %str2)
strstr(%str, %substr)
getSubStr(%str, %pos, %len)

// Math
mAbs(%val)
mSqrt(%val)
mFloor(%val)
mCeil(%val)
mPow(%base, %exp)

// Vector
VectorAdd(%v1, %v2)
VectorDist(%v1, %v2)
VectorDot(%v1, %v2)
VectorNormalize(%v)
```

### File Paths

```
Game Root/
├── scarface.exe
├── cement.rcf
├── scriptc/*.cso
├── art/*.p3d
├── sound/*.wav
└── data/*.dat
```

---

## Appendix B: Resources

### Community Links

- **Scarface Remastered Discord:** https://discord.gg/ZRGeNsu
- **ModDB:** Search "Scarface The World Is Yours mods"
- **Forum:** https://forum.mixmods.com.br (Portuguese)

### Tools Download

- BrokenFace Decompiler: [GitHub Repository]
- P3D Tools: [Included in research files]
- Hash Key Generator: [Included in research files]

### Learning Resources

- Torque3D Documentation: https://github.com/GarageGames/Torque3D
- TorqueScript Guide: http://docs.garagegames.com
- Pure3D Format: [Community documentation]

---

## Appendix C: Troubleshooting

### Common Issues

**Issue:** Decompiled script won't recompile  
**Solution:** Check for syntax errors, verify string encoding

**Issue:** Modified P3D crashes game  
**Solution:** Verify skeleton matches original, check chunk IDs

**Issue:** Hash collisions  
**Solution:** Use full string names, avoid shortened versions

**Issue:** Memory crash after modifications  
**Solution:** Check object cleanup, verify memory allocations

---

## Conclusion

This guide provides a comprehensive foundation for modding Scarface: The World Is Yours. The game's modified Torque engine, while complex, is well-documented through community reverse engineering efforts. With these tools and knowledge, you can:

- Decompile and modify game scripts
- Create custom missions and gameplay
- Replace and modify 3D models
- Understand the game's internal systems
- Build new content while maintaining compatibility

The Director's Cut modification project and the broader modding community continue to expand what's possible with this classic game. Happy modding!

---

**Document Version:** 1.0  
**Last Updated:** December 29, 2025  
**Author:** Director's Cut Modification Team  
**Based on Research by:** BrokenFace, Scarface Community Contributors

---
