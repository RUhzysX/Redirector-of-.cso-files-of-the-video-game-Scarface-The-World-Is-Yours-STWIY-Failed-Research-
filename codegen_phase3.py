#!/usr/bin/env python3
"""
Scarface Code Generator - Phase 3
Objects & Arrays: Field access, array indexing, object creation

Adds to Phases 1 & 2:
- Object field access (object.field, object.field[index])
- Array indexing (array[index], array[index, field])
- Object creation (new ClassName(name) { fields })
- Field assignments
"""

import sys
sys.path.insert(0, '/home/claude/scarface_compiler_v2')

from codegen_phase2 import CodeGenerator as Phase2CodeGen
from compiler_core import ScarfaceCompiler, Opcode
from typing import List, Optional, Dict, Callable

class CodeGenerator(Phase2CodeGen):
    """
    Phase 3: Adds objects & arrays to Phases 1 & 2
    """
    
    def __init__(self, compiler: ScarfaceCompiler):
        super().__init__(compiler)
    
    # ========================================================================
    # OBJECT SELECTION
    # ========================================================================
    
    def emit_setcurobject(self, obj_name: str):
        """
        Emit OP_SETCUROBJECT to select an object by name
        
        Args:
            obj_name: Object name string
        """
        offset = self.get_string_table().add(obj_name)
        
        self.code.emit_opcode(Opcode.OP_SETCUROBJECT)
        self.code.emit_u16_be(offset)
    
    def emit_setcurobject_new(self):
        """
        Emit OP_SETCUROBJECT_NEW
        Selects the most recently created object
        """
        self.code.emit_opcode(Opcode.OP_SETCUROBJECT_NEW)
    
    # ========================================================================
    # FIELD ACCESS
    # ========================================================================
    
    def emit_setcurfield(self, field_name: str):
        """
        Emit OP_SETCURFIELD to select a field
        
        Args:
            field_name: Field name string
        """
        offset = self.get_string_table().add(field_name)
        
        self.code.emit_opcode(Opcode.OP_SETCURFIELD)
        self.code.emit_u16_be(offset)
    
    def emit_setcurfield_array(self, field_name: str):
        """
        Emit OP_SETCURFIELD_ARRAY for array[index, field] access
        
        Note: Index should already be on stack
        
        Args:
            field_name: Field name string
        """
        offset = self.get_string_table().add(field_name)
        
        self.code.emit_opcode(Opcode.OP_SETCURFIELD_ARRAY)
        self.code.emit_u16_be(offset)
    
    def emit_loadfield(self, field_type: str = 'str'):
        """
        Emit OP_LOADFIELD_* to load field value
        
        Args:
            field_type: 'str', 'uint', or 'flt'
        """
        if field_type == 'str':
            self.code.emit_opcode(Opcode.OP_LOADFIELD_STR)
        elif field_type == 'uint':
            self.code.emit_opcode(Opcode.OP_LOADFIELD_UINT)
        elif field_type == 'flt':
            self.code.emit_opcode(Opcode.OP_LOADFIELD_FLT)
        else:
            raise ValueError(f"Unknown field type: {field_type}")
    
    def emit_savefield(self, field_type: str = 'str'):
        """
        Emit OP_SAVEFIELD_* to save value to field
        
        Args:
            field_type: 'str', 'uint', or 'flt'
        """
        if field_type == 'str':
            self.code.emit_opcode(Opcode.OP_SAVEFIELD_STR)
        elif field_type == 'uint':
            self.code.emit_opcode(Opcode.OP_SAVEFIELD_UINT)
        elif field_type == 'flt':
            self.code.emit_opcode(Opcode.OP_SAVEFIELD_FLT)
        else:
            raise ValueError(f"Unknown field type: {field_type}")
    
    # ========================================================================
    # OBJECT CREATION
    # ========================================================================
    
    def emit_create_object(self, class_name: str, obj_name: str = "",
                          is_datablock: bool = False):
        """
        Emit OP_CREATE_OBJECT
        
        Format:
            OP_CREATE_OBJECT (1 byte)
            class_name_offset (2 bytes BE)
            obj_name_offset (2 bytes BE)
            is_datablock (1 byte)
        
        Args:
            class_name: Class name (e.g., "ScriptObject")
            obj_name: Optional object name
            is_datablock: True for datablock, False for object
        """
        class_offset = self.get_string_table().add(class_name)
        name_offset = self.get_string_table().add(obj_name) if obj_name else 0
        
        self.code.emit_opcode(Opcode.OP_CREATE_OBJECT)
        self.code.emit_u16_be(class_offset)
        self.code.emit_u16_be(name_offset)
        self.code.emit_u8(1 if is_datablock else 0)
    
    def emit_end_object(self, add_to_parent: bool = True):
        """
        Emit OP_END_OBJECT
        
        Args:
            add_to_parent: Whether to add object to parent scope
        """
        self.code.emit_opcode(Opcode.OP_END_OBJECT)
        self.code.emit_u8(1 if add_to_parent else 0)
    
    def emit_add_object(self):
        """
        Emit OP_ADD_OBJECT with placeholder end index
        Will be patched when object definition ends
        """
        self.code.emit_opcode(Opcode.OP_ADD_OBJECT)
        
        # Placeholder for end code index
        end_idx_pos = self.code.tell()
        self.code.emit_u8(0)
        
        return end_idx_pos
    
    def patch_object_end(self, end_idx_pos: int):
        """Patch OP_ADD_OBJECT end index"""
        end_code_idx = self.code.code_count
        self.code.data[end_idx_pos] = end_code_idx & 0xFF
        print(f"  [DEBUG] Patched object end at byte {end_idx_pos} to code {end_code_idx}")
    
    # ========================================================================
    # HIGH-LEVEL HELPERS
    # ========================================================================
    
    def emit_field_assignment(self, obj_name: str, field_name: str, 
                             value, field_type: str = 'str'):
        """
        Emit: object.field = value
        
        Args:
            obj_name: Object name
            field_name: Field name
            value: Value to assign
            field_type: 'str', 'uint', or 'flt'
        """
        # Select object
        self.emit_setcurobject(obj_name)
        
        # Select field
        self.emit_setcurfield(field_name)
        
        # Load value
        if field_type == 'str':
            self.emit_load_string_constant(str(value))
        elif field_type == 'uint':
            self.emit_load_uint_constant(int(value))
        elif field_type == 'flt':
            self.emit_load_float_constant(float(value))
        
        # Save to field
        self.emit_savefield(field_type)
    
    def emit_array_field_assignment(self, array_name: str, index_value,
                                   field_name: str, value, 
                                   field_type: str = 'str'):
        """
        Emit: array[index, field] = value
        
        Args:
            array_name: Array object name
            index_value: Index (string or number)
            field_name: Field name
            value: Value to assign
            field_type: 'str', 'uint', or 'flt'
        """
        # Select array object
        self.emit_setcurobject(array_name)
        
        # Load index onto stack
        if isinstance(index_value, str):
            self.emit_setcurvar(index_value)
            self.emit_loadvar('str')
        elif isinstance(index_value, int):
            self.emit_load_uint_constant(index_value)
        else:
            self.emit_load_string_constant(str(index_value))
        
        # Select field with array index
        self.emit_setcurfield_array(field_name)
        
        # Load value
        if field_type == 'str':
            self.emit_load_string_constant(str(value))
        elif field_type == 'uint':
            self.emit_load_uint_constant(int(value))
        elif field_type == 'flt':
            self.emit_load_float_constant(float(value))
        
        # Save to field
        self.emit_savefield(field_type)
    
    def emit_array_field_read(self, array_name: str, index_value,
                             field_name: str, field_type: str = 'str'):
        """
        Emit: value = array[index, field]
        Result is left on stack
        
        Args:
            array_name: Array object name
            index_value: Index (string or number)
            field_name: Field name
            field_type: 'str', 'uint', or 'flt'
        """
        # Select array object
        self.emit_setcurobject(array_name)
        
        # Load index onto stack
        if isinstance(index_value, str):
            self.emit_setcurvar(index_value)
            self.emit_loadvar('str')
        elif isinstance(index_value, int):
            self.emit_load_uint_constant(index_value)
        else:
            self.emit_load_string_constant(str(index_value))
        
        # Select field with array index
        self.emit_setcurfield_array(field_name)
        
        # Load value (leaves on stack)
        self.emit_loadfield(field_type)
    
    def emit_object_with_fields(self, class_name: str, obj_name: str,
                               fields: Dict[str, tuple]):
        """
        Emit complete object creation with fields
        
        Pattern:
            OP_CREATE_OBJECT
            OP_ADD_OBJECT (with end placeholder)
            [field assignments using OP_SETCUROBJECT_NEW]
            OP_END_OBJECT
        
        Args:
            class_name: Class name
            obj_name: Object name
            fields: Dict of field_name -> (value, type)
        """
        # Create object
        self.emit_create_object(class_name, obj_name)
        
        # Start object definition
        end_pos = self.emit_add_object()
        
        # Assign fields
        for field_name, (value, field_type) in fields.items():
            # Select the newly created object
            self.emit_setcurobject_new()
            
            # Select field
            self.emit_setcurfield(field_name)
            
            # Load value
            if field_type == 'str':
                self.emit_load_string_constant(str(value))
            elif field_type == 'uint':
                self.emit_load_uint_constant(int(value))
            elif field_type == 'flt':
                self.emit_load_float_constant(float(value))
            
            # Save to field
            self.emit_savefield(field_type)
        
        # End object
        self.emit_end_object()
        
        # Patch end index
        self.patch_object_end(end_pos)


# ============================================================================
# TEST FUNCTIONS
# ============================================================================

def test_simple_field_access():
    """Test: $myobject.name = "TestObject"; """
    print("="*70)
    print("TEST: Simple Field Assignment")
    print("="*70)
    
    compiler = ScarfaceCompiler()
    gen = CodeGenerator(compiler)
    
    # $myobject.name = "TestObject"
    gen.emit_field_assignment("myobject", "name", "TestObject", 'str')
    
    # Top-level return
    gen.emit_return()
    
    # Save
    output = "test_field_access.cso"
    compiler.compile_to_cso(output)
    
    print(f"\n✓ Created: {output}")
    compiler.dump_info()
    
    return output


def test_array_field_access():
    """Test: myArray[0, "name"] = "Item1"; """
    print("\n" + "="*70)
    print("TEST: Array Field Assignment")
    print("="*70)
    
    compiler = ScarfaceCompiler()
    gen = CodeGenerator(compiler)
    
    # myArray[0, "name"] = "Item1"
    gen.emit_array_field_assignment("myArray", 0, "name", "Item1", 'str')
    
    # myArray[1, "name"] = "Item2"
    gen.emit_array_field_assignment("myArray", 1, "name", "Item2", 'str')
    
    # Top-level return
    gen.emit_return()
    
    # Save
    output = "test_array_access.cso"
    compiler.compile_to_cso(output)
    
    print(f"\n✓ Created: {output}")
    compiler.dump_info()
    
    return output


def test_object_creation():
    """Test: new ScriptObject(TestObj) { field1 = "value"; field2 = 42; }; """
    print("\n" + "="*70)
    print("TEST: Object Creation with Fields")
    print("="*70)
    
    compiler = ScarfaceCompiler()
    gen = CodeGenerator(compiler)
    
    # new ScriptObject(TestObj) { field1 = "value"; field2 = 42; }
    fields = {
        "field1": ("value", 'str'),
        "field2": (42, 'uint'),
    }
    gen.emit_object_with_fields("ScriptObject", "TestObj", fields)
    
    # Top-level return
    gen.emit_return()
    
    # Save
    output = "test_object_create.cso"
    compiler.compile_to_cso(output)
    
    print(f"\n✓ Created: {output}")
    compiler.dump_info()
    
    return output


def test_array_with_variable_index():
    """Test: $i = 0; myArray[$i, "data"] = "test"; """
    print("\n" + "="*70)
    print("TEST: Array Access with Variable Index")
    print("="*70)
    
    compiler = ScarfaceCompiler()
    gen = CodeGenerator(compiler)
    
    # $i = 0
    gen.emit_variable_assignment("$i", 0, var_type='uint')
    
    # myArray[$i, "data"] = "test"
    gen.emit_array_field_assignment("myArray", "$i", "data", "test", 'str')
    
    # Top-level return
    gen.emit_return()
    
    # Save
    output = "test_array_var_index.cso"
    compiler.compile_to_cso(output)
    
    print(f"\n✓ Created: {output}")
    compiler.dump_info()
    
    return output


def test_complex_object_script():
    """
    Test complex script from mission_manager pattern:
    myArray[0, "Name"] = "FF_0";
    myArray[0, "AutoStart"] = 0;
    """
    print("\n" + "="*70)
    print("TEST: Complex Script (Mission Manager Pattern)")
    print("="*70)
    
    compiler = ScarfaceCompiler()
    gen = CodeGenerator(compiler)
    
    # Simulate: $idx = 0
    gen.emit_variable_assignment("$idx", 0, var_type='uint')
    
    # myArray[$idx, "Name"] = "FF_0"
    gen.emit_array_field_assignment("myArray", "$idx", "Name", "FF_0", 'str')
    
    # myArray[$idx, "AutoStart"] = 0
    gen.emit_array_field_assignment("myArray", "$idx", "AutoStart", 0, 'uint')
    
    # myArray[$idx, "WayPoint"] = "-758.22 2.52 541.44"
    gen.emit_array_field_assignment("myArray", "$idx", "WayPoint", 
                                    "-758.22 2.52 541.44", 'str')
    
    # Top-level return
    gen.emit_return()
    
    # Save
    output = "test_complex_array.cso"
    compiler.compile_to_cso(output)
    
    print(f"\n✓ Created: {output}")
    compiler.dump_info()
    
    return output


def verify_with_brokenface(cso_path):
    """Verify by decompiling with BrokenFace"""
    import subprocess
    import os
    
    print(f"\n{'='*70}")
    print(f"VERIFYING: {os.path.basename(cso_path)}")
    print(f"{'='*70}")
    
    result = subprocess.run(
        ['python3', 'brokenface/decompile.py', cso_path],
        cwd="/home/claude/BrokenFace-master's File Extractor",
        capture_output=True,
        text=True
    )
    
    if "Successfully decompiled" in result.stdout:
        print("✅ BrokenFace: SUCCESS")
        
        # Read decompiled output
        cs_path = cso_path + '.cs'
        if os.path.exists(cs_path):
            with open(cs_path, 'r') as f:
                decompiled = f.read()
            
            print("\nDecompiled output:")
            for line in decompiled.split('\n')[:30]:
                print(f"  {line}")
            
            return True
        else:
            print(f"⚠️  Output file not found: {cs_path}")
            return False
    else:
        print("❌ BrokenFace: FAILED")
        if "ERROR" in result.stdout:
            for line in result.stdout.split('\n'):
                if "ERROR" in line:
                    print(f"  {line}")
        return False


if __name__ == '__main__':
    print("SCARFACE CODE GENERATOR - PHASE 3")
    print("Objects & Arrays: Field access, object creation")
    print()
    
    tests = [
        ("Simple Field Access", test_simple_field_access),
        ("Array Field Access", test_array_field_access),
        ("Object Creation", test_object_creation),
        ("Array with Variable Index", test_array_with_variable_index),
        ("Complex Array Script", test_complex_object_script),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            output = test_func()
            success = verify_with_brokenface(output)
            results.append((name, success))
        except Exception as e:
            print(f"\n❌ ERROR in {name}: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # Summary
    print("\n" + "="*70)
    print("PHASE 3 TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Phase 3 is working!")
        print("\nPhase 3 Complete - We now have:")
        print("  ✅ Variables (global & local)")
        print("  ✅ Functions with parameters")
        print("  ✅ Comparisons & arithmetic")
        print("  ✅ If/else statements")
        print("  ✅ While loops")
        print("  ✅ Object field access")
        print("  ✅ Array indexing")
        print("  ✅ Object creation")
        print("\n📊 Estimated coverage: ~85-90% of real game scripts!")
    elif passed >= total * 0.6:
        print(f"\n✨ Good progress! {passed}/{total} tests passing.")
        print(f"📊 Estimated coverage: ~70-80% of game scripts")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Need more work.")
