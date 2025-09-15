# interpreter.py
import sys
import re

class ReturnValue(Exception):
    """Custom exception to handle function returns"""
    def __init__(self, value):
        self.value = value

class PebbleInterpreter:
    def __init__(self):
        self.variables = {}
        self.functions = {}
        self.commands = {
            "say": self.cmd_say,
            "type": self.cmd_type,
        }

    def run(self, filename):
        with open(filename, "r") as f:
            lines = f.readlines()
        self.execute_block(lines)

    def execute_block(self, lines, start=0, end=None, local_vars=None, top_level=True):
        """Execute a block of Pebble code"""
        if local_vars is None:
            local_vars = {}

        i = start
        while i < (end if end else len(lines)):
            line = lines[i].rstrip("\n")
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                i += 1
                continue

            # function definition
            if stripped.startswith("fnc "):
                name, args, body, new_i = self.parse_function(lines, i)
                self.functions[name] = (args, body)
                i = new_i
                continue

            # if statement
            if stripped.startswith("if "):
                condition, body, new_i = self.parse_if(lines, i)
                if self.evaluate_condition(condition, local_vars):
                    try:
                        self.execute_block(body, 0, len(body), local_vars.copy(), top_level=False)
                    except ReturnValue as rv:
                        return rv.value
                i = new_i
                continue

            # variable assignment
            if " is " in stripped:
                name, value = stripped.split(" is ", 1)
                self.variables[name.strip()] = self.evaluate_expr(value.strip(), local_vars)
                i += 1
                continue

            # return statement
            if stripped.startswith("out "):
                value = self.evaluate_expr(stripped[4:], local_vars)
                raise ReturnValue(value)

            # built-in commands
            parts = stripped.split(maxsplit=1)
            cmd = parts[0]
            args = parts[1] if len(parts) > 1 else ""
            if cmd in self.commands:
                self.commands[cmd](args, local_vars)
                i += 1
                continue

            # function call (top-level)
            if "(" in stripped and stripped.endswith(")"):
                result = self.evaluate_expr(stripped, local_vars)
                if top_level and result is not None:
                    print(result)
                i += 1
                continue

            # unknown
            print(f"Unknown command: {stripped}")
            i += 1

    # ------------------- Parsing Helpers -------------------

    def parse_function(self, lines, index):
        header = lines[index].strip()
        _, rest = header.split(" ", 1)  # remove "fnc"
        name, args = rest.split("(", 1)
        name = name.strip()
        args = args[:-2].strip() if args.endswith("):") else args[:-1].strip()
        args = [a.strip() for a in args.split(",")] if args else []

        body = []
        i = index + 1
        while i < len(lines):
            if lines[i].startswith("    "):  # 4-space indentation
                body.append(lines[i][4:])
                i += 1
            else:
                break
        return name, args, body, i

    def parse_if(self, lines, index):
        header = lines[index].strip()
        condition = header[3:-1].strip()  # strip 'if ' and ':'
        body = []
        i = index + 1
        while i < len(lines):
            if lines[i].startswith("    "):
                body.append(lines[i][4:])
                i += 1
            else:
                break
        return condition, body, i

    # ------------------- Execution Helpers -------------------

    def evaluate_expr(self, expr, local_vars):
        """Evaluate an expression that may contain nested Pebble function calls, variables, or literals"""
        expr = expr.strip()
        # function call pattern: funcname(args)
        func_call_pattern = re.compile(r"^([a-zA-Z_]\w*)\((.*)\)$")
        match = func_call_pattern.match(expr)
        if match:
            name = match.group(1)
            args_str = match.group(2)
            args = self.split_args(args_str)
            evaluated_args = [self.evaluate_expr(a, local_vars) for a in args]
            return self.call_function(f"{name}({', '.join(map(str, evaluated_args))})", local_vars)
        # variable
        if expr in local_vars:
            return local_vars[expr]
        if expr in self.variables:
            return self.variables[expr]
        # literal or number
        try:
            return eval(expr, {}, {**self.variables, **local_vars})
        except Exception:
            return expr  # fallback as string

    def split_args(self, args_str):
        """Split function arguments by commas, handling nested parentheses"""
        args = []
        current = ""
        depth = 0
        for char in args_str:
            if char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
            elif char == "," and depth == 0:
                args.append(current.strip())
                current = ""
                continue
            current += char
        if current:
            args.append(current.strip())
        return args

    def evaluate_condition(self, condition, local_vars):
        tokens = condition.split()
        if len(tokens) != 3:
            return False
        left = self.evaluate_expr(tokens[0], local_vars)
        op = tokens[1]
        right = self.evaluate_expr(tokens[2], local_vars)

        if op == "bigger":
            return left > right
        elif op == "smaller":
            return left < right
        elif op == "equal":
            return left == right
        else:
            return False

    def call_function(self, call, local_vars):
        name, args = call.split("(", 1)
        name = name.strip()
        args = args[:-1].strip()
        args = [a.strip() for a in args.split(",")] if args else []

        if name not in self.functions:
            print(f"Unknown function: {name}")
            return None

        fn_args, body = self.functions[name]
        new_locals = local_vars.copy()
        for i, arg_name in enumerate(fn_args):
            if i < len(args):
                new_locals[arg_name] = args[i] if not isinstance(args[i], str) else self.evaluate_expr(args[i], local_vars)

        try:
            return self.execute_block(body, 0, len(body), new_locals, top_level=False)
        except ReturnValue as rv:
            return rv.value

    # ------------------- Built-in Commands -------------------

    def cmd_say(self, args, local_vars):
        if args.startswith('"') and args.endswith('"'):
            print(args[1:-1])
        else:
            value = self.evaluate_expr(args, local_vars)
            print(value)

    def cmd_type(self, args, local_vars):
        value = self.evaluate_expr(args, local_vars)
        print(type(value).__name__)

# ------------------- Entry Point -------------------

def main():
    if len(sys.argv) < 2:
        print("Usage: pebble file.pb")
    else:
        PebbleInterpreter().run(sys.argv[1])

if __name__ == "__main__":
    main()
