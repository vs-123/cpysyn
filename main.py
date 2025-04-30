import ast, sys

output_file_opened = ""
counter = 0
tab_count = 0

def write_to_output_file(str):
    global output_file_opened
    output_file_opened.write(str)

def built_in_write_memory(args):
    global counter

    # Volatile types
    write_to_output_file(
        f"volatile {python_type_to_c_type(args[2].id)} *buf{counter}=({python_type_to_c_type(args[2].id)}*)"
    )
    code_generation_expression(args[0])
    write_to_output_file(";\n")
    write_to_output_file(f"*buf{counter} = ")
    code_generation_expression(args[1])
    
    counter += 1
    return

def asm_volatile(args):
    write_to_output_file(f"asm volatile (\"{args[0].value}\")")

def pointer(args):
    write_to_output_file(f"*{args[0].id}")

built_in_functions = {
    "__builtin_write_mem" : built_in_write_memory,
    "asm" : asm_volatile,
    "__pointer": pointer,
}

def code_generation_function_call(called_function):
    if called_function.func.id not in built_in_functions:
        write_to_output_file("    "*tab_count+f"{called_function.func.id}(")

        for arg in called_function.args:
            code_generation_expression(arg)
            if arg != called_function.args[-1]:
                write_to_output_file(",")

        write_to_output_file(")")
    else:
        built_in_functions[called_function.func.id](called_function.args)


def code_generation_operator(op):
    match op.__class__:
        case ast.Add:
            write_to_output_file("+")
        case ast.Sub:
            write_to_output_file("-")
        case ast.Mult:
            write_to_output_file("*")
        case ast.Div:
            write_to_output_file("/")
        case ast.Mod:
            write_to_output_file("%")
        case ast.LShift:
            write_to_output_file("<<")
        case ast.RShift:
            write_to_output_file(">>")
        case ast.BitOr:
            write_to_output_file("|")
        case ast.BitXor:
            write_to_output_file("^")
        case ast.BitAnd:
            write_to_output_file("&")

def code_generation_boolean_operator(operator):
    match type(operator):
        case ast.And:
            write_to_output_file(" && ")
        case ast.Or:
            write_to_output_file(" || ")
        case ast.Not:
            write_to_output_file("!")

def code_generation_conditional_operator(operator):
    match type(operator):
        case ast.Eq:
            write_to_output_file("==")
        case ast.NotEq:
            write_to_output_file("!=")
        case ast.Lt:
            write_to_output_file("<")
        case ast.LtE:
            write_to_output_file("<=")
        case ast.Gt:
            write_to_output_file(">")
        case ast.GtE:
            write_to_output_file(">=")
        case _:
            # Not supported In, Is, etc.
            pass

def code_generation_expression(node):
    match node.__class__:
        case ast.Constant:
            if type(node.value) == str:
                if len(node.value) >= 2:
                    new_string = node.value.replace("\n", "\\n")
                    write_to_output_file(f"\"{new_string}\"")
                else:
                    write_to_output_file(f"\'{node.value}\'")
            else:
                write_to_output_file(f"{node.value}")

        # Identifier
        case ast.Name:
            write_to_output_file(f"{node.id}")
        
        # List
        case ast.List:
            write_to_output_file("{")
            for i in node.elts:
                code_generation_expression(i)
                if i != node.elts[-1]:
                    write_to_output_file(",")
            write_to_output_file("}")

        # Operations
        case ast.BinOp:
            code_generation_expression(node.left)
            code_generation_operator(node.op)
            code_generation_expression(node.right)

        # Function calls
        case ast.Call:
            code_generation_function_call(node)

        case ast.Subscript:
            code_generation_expression(node.value)
            write_to_output_file("[")
            code_generation_expression(node.slice)
            write_to_output_file("]")
        
        case ast.Compare:
            if len(node.ops) > 1:
                raise Exception("Chained conditional operators not supported yet")
            code_generation_expression(node.left)
            write_to_output_file(" ")
            code_generation_conditional_operator(node.ops[0])
            write_to_output_file(" ")
            code_generation_expression(node.comparators[0])

        case ast.BoolOp:
            for (i, value) in enumerate(node.values):
                code_generation_expression(value)
                if i != len(node.values)-1:
                    code_generation_boolean_operator(node.op)
                    

def code_generation_subscript(node, name=""):
    match node.value.id:
        case "list":
            write_to_output_file(f"{python_type_to_c_type(node.slice.id)} {name}[]")

def python_type_to_c_type(python_type: str):
    match python_type:
        case "int" | "float" | "char":
            return python_type
        case "u8" | "u16" | "u32" | "u64":
            return f"uint{python_type[1:]}_t"
        
        case "str":
            return "char*"
        case "bool":
            return "int"
        
        # Other types will be regarded as void
        case _:
            return "void"

def code_generation_annotation(type_annotation, arg):
    match type_annotation.__class__:
        case ast.Name:
            return write_to_output_file(python_type_to_c_type(type_annotation.id) + " " + arg)
        case ast.Subscript:
            return code_generation_subscript(type_annotation, arg)

def code_generation_args(args):
    for arg in args:
        code_generation_annotation(arg.annotation, arg.arg)

        if arg != args[-1]:
            write_to_output_file(", ")

def code_generation_define_function(node):
    global tab_count
    # TYPE NAME(TYPE ARG1, TYPE ARG2) {
    if isinstance(node.returns, ast.Constant) or node.returns is None:
        write_to_output_file("    "*tab_count+f"void {node.name}(")
    else:
        write_to_output_file(f"{python_type_to_c_type(node.returns.id)} {node.name}(")

    code_generation_args(node.args.args)

    write_to_output_file(") {\n")
    
    # Body
    tab_count += 1
    for item in node.body:
        code_generation_node(item)

    write_to_output_file("}\n")

def code_generation_annotated_assign(node):
    write_to_output_file("    "*tab_count)
    code_generation_annotation(node.annotation, node.target.id)

    write_to_output_file(f" = ")

    code_generation_expression(node.value)

def code_generation_assign(node):
    write_to_output_file("    "*tab_count+f"{node.targets[0].id} = ")
    code_generation_expression(node.value)

def code_generation_for_loops(node):
    write_to_output_file("for (")
    if isinstance(node.iter, ast.Call):
        if node.iter.func.id == "range":
            step = node.iter.args[2].value if len(node.iter.args) == 3 else 1

            # int x = ?; x < ?; x += ?
            write_to_output_file(f"int {node.target.id} = ")
            code_generation_expression(node.iter.args[0])
            write_to_output_file(f"; {node.target.id} < ")
            code_generation_expression(node.iter.args[1])
            write_to_output_file(f";{node.target.id} += {step})\n{{\n")
        else:
            code_generation_function_call(node.iter)
    else:
           write_to_output_file(f"int __list_iter = 0; __list_iter < sizeof({node.iter.id})/sizeof(*{node.iter.id}); __list_iter++)\n{{\n typeof(*{node.iter.id}) {node.target.id} = {node.iter.id}[__list_iter];\n")


    for i in node.body:
        code_generation_node(i)

    write_to_output_file("}\n")

def code_generation_while_loops(node):
    write_to_output_file("while (")
    code_generation_expression(node.test)
    write_to_output_file(") {\n")

    for inner_node in node.body:
        code_generation_node(inner_node)

    write_to_output_file("}\n")

def code_generation_if_else(node):
    global tab_count
    # If part
    write_to_output_file("    "*tab_count+"if (")
    code_generation_expression(node.test)
    write_to_output_file(") {\n")

    # Body
    tab_count+=1
    for inner_node in node.body:
        code_generation_node(inner_node)
    tab_count-=1

    # Else
    if len(node.orelse) > 0:
        write_to_output_file("    "*tab_count+"}")
        write_to_output_file(" else {\n")
        tab_count+=1
        for inner_node in node.orelse:
            code_generation_node(inner_node)
        tab_count-=1
        write_to_output_file("    "*tab_count+"}\n")
    else:
        write_to_output_file("\n")

def code_generation_node(node):
    match node.__class__:
        # Functions
        case ast.FunctionDef:
            code_generation_define_function(node)

        # Assignments with explicit types
        case ast.AnnAssign:
            code_generation_annotated_assign(node)
            write_to_output_file(";\n")
        
        # For reassignments
        case ast.Assign:
            code_generation_assign(node)
            write_to_output_file(";\n")

        # Operator assignment
        case ast.AugAssign:
            code_generation_expression(node.target)
            write_to_output_file(" ")
            code_generation_operator(node.op)
            write_to_output_file("= ")
            code_generation_expression(node.value)
            write_to_output_file(";\n")

        # Normal expressions        
        case ast.Expr:
            code_generation_expression(node.value)
            write_to_output_file(";\n")

        # Return
        case ast.Return:
            write_to_output_file("    "*tab_count+"return ")
            code_generation_expression(node.value)
            write_to_output_file(";\n")

        # For loops
        case ast.For:
            code_generation_for_loops(node)
        
        case ast.While:
            code_generation_while_loops(node)

        # Import
        case ast.Import:
            for import_item in node.names:
                write_to_output_file(f"#include \"{import_item.name}.h\"\n")

        case ast.If:
            code_generation_if_else(node)


def code_generation(parsed_code, debug_mode=False):
    for node in parsed_code.body:
        code_generation_node(node)

    if debug_mode:
        print(ast.dump(parsed_code))

def main():
    global output_file_opened
    source_code = ""

    if len(sys.argv) == 3:
        try:
            with open(sys.argv[1], "r") as input:
                source_code = input.read()
                output_file_opened = open(sys.argv[2], "w")
                parsed = ast.parse(source_code)
                code_generation(parsed)
        except FileNotFoundError as error:
            print(f"Cannot read file '{sys.argv[1]}': {error}")
    else:
        print(f"USAGE: {sys.argv[0]} <source_code_file> <output_file>")

if __name__ == "__main__":
    main()