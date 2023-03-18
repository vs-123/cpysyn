# cpysyn
C with Python syntax

## Why?
idk

## Features and Limitations
Transpiles Python-syntaxed C to C (1 to 1)

Needs type annotations for the C code to work properly (has no support for assignments without types)

Can assign unsigned integer types using `u8`, `u16`, `u32` and `u64`

All imports are automatically imported as local header files (no support for taking in standard library imports like `<stdio>`, `<math.h>`, etc.)

Doesn't have error checking lol

## Example
You can find examples at `examples/` directory.

### Cursed?
cursed.