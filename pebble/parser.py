import sys

class PebbleParser:
    def __init__(self):
        self.variables = {}
        self.functions = {}

    def evaluate_expression(self, expr):
        expr = expr.strip()
        if not expr:
            return None
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
            return [self.evaluate_expression(i.strip()) for i in items if i.strip()]
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
        if expr.startswith("inp[") and expr.endswith("]"):
            prompt = self.evaluate_expression(expr[4:-1].strip())
            return input(prompt)
        if "[" in expr and expr.endswith("]"):
            var_name, idx_part = expr.split("[", 1)
            idx_expr = idx_part[:-1]
            container = self.variables.get(var_name.strip())
            index = self.evaluate_expression(idx_expr.strip())
            return container[index]
        if expr in self.variables:
            return self.variables[expr]
        try:
            expr = expr.replace("^", "**")
            return eval(expr, {"__builtins__": {}}, self.variables)
        except Exception:
            raise Exception(f"Could not evaluate expression: {expr}")

    def execute_line(self, line):
        line = line.strip()
        if not line or line.startswith("!"):
            return
        if line.startswith("say "):
            value = self.evaluate_expression(line[4:].strip())
            print(value)
        elif " is " in line:
            var, expr = line.split(" is ", 1)
            var = var.strip()
            self.variables[var] = self.evaluate_expression(expr)
        elif line.startswith("fnc "):
            name_part = line[4:].strip()
            name, rest = name_part.split("(", 1)
            args = rest.split(")")[0].split(",")
            args = [a.strip() for a in args if a.strip()]
            self.functions[name.strip()] = {"args": args, "body": []}
            self.current_function = name.strip()
            self.in_function = True
        elif line.startswith("type "):
            value = self.evaluate_expression(line[5:].strip())
            self.return_value = value
            self.in_return = True
        elif line.startswith("go ") and " in " in line:
            before, after = line[3:].split(" in ", 1)
            var = before.strip()
            iterable = self.evaluate_expression(after.strip().rstrip(":"))
            self.loop_var = var
            self.loop_items = iterable
            self.in_loop = True
        elif line.endswith(":"):
            pass
        elif "(" in line and line.endswith(")"):
            name = line.split("(", 1)[0].strip()
            args_raw = line.split("(", 1)[1].rstrip(")")
            args = []
            if args_raw.strip():
                args = [self.evaluate_expression(a.strip()) for a in args_raw.split(",")]
            if name in self.functions:
                func = self.functions[name]
                local_vars = self.variables.copy()
                for i, arg in enumerate(func["args"]):
                    if i < len(args):
                        local_vars[arg] = args[i]
                parser = PebbleParser()
                parser.variables = local_vars
                for b in func["body"]:
                    parser.execute_line(b)
                    if getattr(parser, "in_return", False):
                        return parser.return_value
            else:
                raise Exception(f"Unknown function: {name}")
        else:
            raise Exception(f"Unknown syntax: {line}")

    def execute_block(self, block):
        i = 0
        while i < len(block):
            line = block[i].rstrip()
            if not line.strip():
                i += 1
                continue
            if line.startswith("fnc "):
                name_part = line[4:].strip()
                name, rest = name_part.split("(", 1)
                args = rest.split(")")[0].split(",")
                args = [a.strip() for a in args if a.strip()]
                body = []
                i += 1
                while i < len(block) and (block[i].startswith("    ") or not block[i].strip()):
                    if block[i].strip():
                        body.append(block[i][4:])
                    i += 1
                self.functions[name.strip()] = {"args": args, "body": body}
                continue
            elif line.startswith("go ") and " in " in line:
                before, after = line[3:].split(" in ", 1)
                var = before.strip()
                iterable = self.evaluate_expression(after.strip().rstrip(":"))
                i += 1
                body = []
                while i < len(block) and (block[i].startswith("    ") or not block[i].strip()):
                    if block[i].strip():
                        body.append(block[i][4:])
                    i += 1
                for item in iterable:
                    self.variables[var] = item
                    self.execute_block(body)
                continue
            else:
                self.execute_line(line)
                i += 1

    def run(self, code):
        lines = code.split("\n")
        self.execute_block(lines)

def main():
    if len(sys.argv) < 2:
        print("Usage: pebble <file.pb>")
        sys.exit(1)
    path = sys.argv[1]
    with open(path, "r", encoding="utf-8") as f:
        code = f.read()
    parser = PebbleParser()
    parser.run(code)

if __name__ == "__main__":
    main()
