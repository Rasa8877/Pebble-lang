import sys

class ReturnValue(Exception):
    def __init__(self, value):
        self.value = value

class PebbleInterpreter:
    def __init__(self):
        self.variables = {}
        self.functions = {}
        self.builtins = {
            "say": self.execute_builtin,
            "inp": self.execute_builtin,
        }

    def run(self, filename):
        with open(filename, "r") as f:
            lines = f.readlines()
        try:
            self.execute_block(lines)
        except ReturnValue as rv:
            print(rv.value)
        except Exception as e:
            print(f"[Pebble Error] {e}")

    def execute_block(self, lines, indent_level=0):
        i = 0
        while i < len(lines):
            raw_line = lines[i].rstrip("\n").replace("\t", "    ")
            line = raw_line.strip()
            if not line or line.startswith("!"):
                i += 1
                continue

            current_indent = len(raw_line) - len(raw_line.lstrip(" "))
            if current_indent < indent_level:
                return i

            consumed = self.execute_line(line, lines[i+1:], current_indent + 2)
            i += consumed + 1

    def execute_line(self, line, following_lines, next_indent_level):
        line = line.strip()
        if not line:
            return 0

        if line.startswith("say "):
            exprs = line[4:].split(",")
            values = [self.evaluate_expression(e.strip()) for e in exprs]
            print(*values)
            return 0

        if line.startswith("inp[") and line.endswith("]"):
            prompt = self.evaluate_expression(line[4:-1].strip())
            input(prompt)
            return 0

        if line.startswith("fnc "):
            name, rest = line[4:].split("(", 1)
            name = name.strip()
            params = rest.split(")")[0].split(",") if ")" in rest else []
            params = [p.strip() for p in params if p.strip()]
            body_start = self.find_block(following_lines, next_indent_level)
            body = following_lines[:body_start]
            self.functions[name] = (params, body)
            return body_start

        if line.startswith("out "):
            value = self.evaluate_expression(line[4:].strip())
            raise ReturnValue(value)

        if line.startswith("if "):
            if ":" in line:
                cond, stmt = line[3:].split(":", 1)
                if self.evaluate_condition(cond.strip()):
                    self.execute_line(stmt.strip(), following_lines, next_indent_level)
            else:
                cond = line[3:].strip()
                if self.evaluate_condition(cond):
                    self.execute_block(following_lines, next_indent_level)
            return 0

        if line.startswith("until "):
            cond_expr = line[6:].strip().rstrip(":")
            block_len = self.find_block(following_lines, next_indent_level)
            block = following_lines[:block_len]
            while self.evaluate_condition(cond_expr):
                self.execute_block(block, next_indent_level)
            return block_len

        if line.startswith("go "):
            parts = line[3:].split(" in ", 1)
            var, collection = parts
            var = var.strip()
            collection = collection.strip().rstrip(":")
            collection_val = self.evaluate_expression(collection)
            block_len = self.find_block(following_lines, next_indent_level)
            block = following_lines[:block_len]
            for val in collection_val:
                self.variables[var] = val
                self.execute_block(block, next_indent_level)
            return block_len

        if " is " in line:
            var, expr = line.split(" is ", 1)
            self.variables[var.strip()] = self.evaluate_expression(expr.strip())
            return 0

        if "(" in line and line.endswith(")"):
            fn_name, arg_str = line.split("(", 1)
            fn_name = fn_name.strip()
            args = [self.evaluate_expression(a.strip()) for a in arg_str[:-1].split(",")] if arg_str[:-1].strip() else []
            if fn_name in self.functions:
                self.call_function(fn_name, args)
            elif fn_name in self.builtins:
                self.execute_builtin(fn_name, args)
            else:
                raise Exception(f"Unknown function: {fn_name}")
            return 0

        return 0

    def evaluate_condition(self, cond):
        cond = cond.replace("big", ">").replace("sml", "<").replace("eql", "==")
        cond = cond.replace("^", "**")
        return eval(cond, {}, self.variables)

    def evaluate_expression(self, expr):
        expr = expr.strip()
        if not expr:
            return None

        expr = expr.replace("^", "**")

        if (expr.startswith('"') and expr.endswith('"')) or (expr.startswith("'") and expr.endswith("'")):
            return expr[1:-1]

        if expr.isdigit():
            return int(expr)
        try:
            return float(expr)
        except ValueError:
            pass

        if expr in ("true", "false"):
            return expr == "true"

        if expr.startswith("{") and expr.endswith("}"):
            items = expr[1:-1].split(",")
            return [self.evaluate_expression(i.strip()) for i in items]

        if expr.startswith("[") and expr.endswith("]"):
            items = expr[1:-1].split(",")
            d = {}
            for item in items:
                if ":" not in item:
                    raise Exception(f"Invalid dictionary item: {item}")
                k, v = item.split(":", 1)
                key = self.evaluate_expression(k.strip())
                value = self.evaluate_expression(v.strip())
                d[key] = value
            return d

        if expr in self.variables:
            return self.variables[expr]

        if "(" in expr and expr.endswith(")"):
            fn_name, arg_str = expr.split("(", 1)
            fn_name = fn_name.strip()
            arg_str = arg_str[:-1]
            args = [self.evaluate_expression(a.strip()) for a in arg_str.split(",")] if arg_str else []
            if fn_name in self.functions:
                return self.call_function(fn_name, args)
            elif fn_name in self.builtins:
                return self.execute_builtin(fn_name, args)
            else:
                raise Exception(f"Unknown function: {fn_name}")

        try:
            return eval(expr, {}, self.variables)
        except Exception:
            raise Exception(f"Could not evaluate expression: {expr}")

    def call_function(self, name, args):
        params, body = self.functions[name]
        backup = self.variables.copy()
        self.variables.update(dict(zip(params, args)))
        try:
            self.execute_block(body, indent_level=2)
        except ReturnValue as rv:
            self.variables = backup
            return rv.value
        self.variables = backup

    def execute_builtin(self, name, args):
        if name == "say":
            print(*args)
            return None
        if name == "inp":
            prompt = args[0] if args else ""
            return input(prompt)
        raise Exception(f"Unknown builtin: {name}")

    def find_block(self, lines, indent_level):
        for i, line in enumerate(lines):
            raw_line = line.replace("\t", "    ")
            if raw_line.strip() and (len(raw_line) - len(raw_line.lstrip(" "))) < indent_level:
                return i
        return len(lines)

def main():
    if len(sys.argv) < 2:
        print("Usage: pebble <file.pb>")
        sys.exit(1)
    PebbleInterpreter().run(sys.argv[1])

if __name__ == "__main__":
    main()
