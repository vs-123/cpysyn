# cpysyn
C with Python syntax

inspired from [snek](https://github.com/Abb1x/snek)

## Why?
it's cursed and cool

## Features and Limitations
- Transpiles Python-syntaxed C to C (1 to 1)

- Needs type annotations for the C code to work properly, cannot work without types (can work but only with reassignments)

- Can assign unsigned integer types using `u8`, `u16`, `u32` and `u64`

- Imports are supported. `import abcd` will be transpiled into `#include "abcd.h"`

- This also has support for assembly volatiles and volatiles using `asm()` and `__builtin_write_mem()` which are built in.

- Doesn't have error checking lol

## Example
You can find examples at `examples/` directory.
