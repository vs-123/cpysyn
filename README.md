# cpysyn
C with Python syntax

inspired from [snek](https://github.com/Abb1x/snek)

## Why?
it's cursed and cool

## Features and Limitations
Transpiles Python-syntaxed C to C (1 to 1)

Needs type annotations for the C code to work properly, cannot work without types (can work but only with reassignments)

Can assign unsigned integer types using `u8`, `u16`, `u32` and `u64`

All imports are automatically imported as local header files (no support for taking in standard library imports like `<stdio>`, `<math.h>`, etc. and will import them as `"stdio.h"`, `"math.h"`, etc.)

This also has support for assembly volatiles and volatiles using `asm()` and `__builtin_write_mem()` which are built in.

Doesn't have error checking lol

## Example
You can find examples at `examples/` directory.
