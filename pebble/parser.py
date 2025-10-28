import sys

class PebbleParser:
    def __init__(self):
        self.variables = {}
        self.functions = {}
        self.builtins = {
            "say": self.builtin_say,
            "inp": self.builtin_inp
        }

    def builtin_say(self, *args):
        print(*args)

    def builtin_inp(self, prompt=""):
        return input(prompt)

    def parse(self, lines):
        blocks = []
        i = 0
        while i < len(lines):
            line = lines[i]
            if not line.strip() or line.strip().startswith("#"):
                i += 1
                continue
            indent = len(line) - len(line.lstrip())
            content = line.strip()
            if content.endswith(":"):
                block_lines = []
                i += 1
                while i < len(lines):
                    next_line = lines[i]
                    next_indent = len(next_line) - len(next_line.lstrip())
                    if next_indent <= indent:
                        break
                    block_lines.append(next_line[indent+4:])
                    i += 1
                blocks.append((content[:-1].strip(), block_lines))
            else:
                blocks.append((content, []))
                i += 1
        return blocks

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
            items = [p for p in self._split_commas(expr[1:-1])]
            return [self.evaluate_expression(i.strip()) for i in items if i.strip()]
        if expr.startswith("[") and expr.endswith("]"):
            items = [p for p in self._split_commas(expr[1:-1])]
            d = {}
            for item in items:
                if ":" not in item:
                    raise Exception(f"Invalid dictionary item: {item}")
                k, v = item.split(":", 1)
                key_token = k.strip()
                if (key_token.startswith('"') and key_token.endswith('"')) or (key_token.startswith("'") and key_token.endswith("'")):
                    key = self.evaluate_expression(key_token)
                elif key_token.isdigit():
                    key = int(key_token)
                else:
                    key = key_token
                value = self.evaluate_expression(v.strip())
                d[key] = value
            return d
        if expr in self.variables:
            return self.variables[expr]
        if expr.startswith("inp[") and expr.endswith("]"):
            prompt = self.evaluate_expression(expr[4:-1].strip())
            return input(prompt)
        if "[" in expr and expr.endswith("]"):
            var, idx = expr.split("[", 1)
            var = var.strip()
            idx = idx[:-1].strip()
            container = self.evaluate_expression(var)
            key = self.evaluate_expression(idx)
            try:
                return container[key]
            except Exception:
                raise Exception(f"Could not index into {var} with key {idx}")
        if "(" in expr and expr.endswith(")"):
            fn_name, arg_str = expr.split("(", 1)
            fn_name = fn_name.strip()
            arg_str = arg_str[:-1]
            args = [self.evaluate_expression(a.strip()) for a in self._split_commas(arg_str)] if arg_str else []
            if fn_name in self.functions:
                return self.call_function(fn_name, args)
            elif fn_name in self.builtins:
                return self.execute_builtin(fn_name, args)
            else:
                raise Exception(f"Unknown function: {fn_name}")
        try:
            return eval(expr, {"__builtins__": {}}, self.variables)
        except Exception:
            raise Exception(f"Could not evaluate expression: {expr}")

    def _split_commas(self, text):
        parts = []
        current = ""
        depth = 0
        in_str = None
        i = 0
        while i < len(text):
            ch = text[i]
            if ch in ('"', "'"):
                if in_str is None:
                    in_str = ch
                elif in_str == ch:
                    in_str = None
                current += ch
            elif ch == "(" and in_str is None:
                depth += 1
                current += ch
            elif ch == ")" and in_str is None:
                depth -= 1
                current += ch
            elif ch == "[" and in_str is None:
                depth += 1
                current += ch
            elif ch == "]" and in_str is None:
                depth -= 1
                current += ch
            elif ch == "," and in_str is None and depth == 0:
                parts.append(current)
                current = ""
            else:
                current += ch
            i += 1
        if current != "":
            parts.append(current)
        return parts

    def execute_builtin(self, name, args):
        if name not in self.builtins:
            raise Exception(f"Unknown builtin: {name}")
        return self.builtins[name](*args)

    def call_function(self, name, args):
        params, body = self.functions[name]
        if len(args) != len(params):
            raise Exception(f"Function {name} expected {len(params)} args, got {len(args)}")
        saved_vars = self.variables.copy()
        for p, a in zip(params, args):
            self.variables[p] = a
        result = self.execute_block(body)
        self.variables = saved_vars
        return result

    def execute_line(self, line):
        if line.startswith("say "):
            exprs = [p for p in self._split_commas(line[4:])]
            values = [self.evaluate_expression(e.strip()) for e in exprs]
            print(*values)
        elif line.startswith("inp[") and line.endswith("]"):
            prompt = self.evaluate_expression(line[4:-1].strip())
            input(prompt)
        elif line.startswith("inp "):
            parts = line[4:].split(" is ", 1)
            if len(parts) != 2:
                raise Exception("Invalid input syntax")
            var_name, prompt_expr = parts[0].strip(), parts[1].strip()
            prompt = self.evaluate_expression(prompt_expr)
            self.variables[var_name] = input(prompt)
        elif " is " in line:
            var, expr = line.split(" is ", 1)
            var = var.strip()
            expr = expr.strip()
            self.variables[var] = self.evaluate_expression(expr)
        elif line.startswith("fnc "):
            name_part, rest = line[4:].split("(", 1)
            fn_name = name_part.strip()
            params = rest.split(")", 1)[0]
            param_list = [p.strip() for p in params.split(",") if p.strip()]
            self.functions[fn_name] = (param_list, [])
            self.current_fn = fn_name
        elif line.startswith("out "):
            expr = line[4:].strip()
            return self.evaluate_expression(expr)
        elif line.startswith("if "):
            cond = line[3:].strip()
            cond = cond.replace("bigger", ">").replace("smaller", "<").replace("equal", "==")
            try:
                if eval(cond, {"__builtins__": {}}, self.variables):
                    return "EXEC_BLOCK"
            except Exception:
                raise Exception(f"Invalid condition: {cond}")
        elif line.startswith("until "):
            cond = line[6:].strip()
            cond = cond.replace("bigger", ">").replace("smaller", "<").replace("equal", "==")
            return ("UNTIL", cond)
        elif line.startswith("go "):
            var_name, rest = line[3:].split(" in ", 1)
            iterable = self.evaluate_expression(rest.strip().rstrip(":"))
            return ("GO", var_name.strip(), iterable)
        else:
            if "(" in line and line.endswith(")"):
                return self.evaluate_expression(line)
            raise Exception(f"Unknown syntax: {line}")

    def execute_block(self, lines):
        i = 0
        result = None
        while i < len(lines):
            line = lines[i]
            res = self.execute_line(line)
            if isinstance(res, tuple) and res[0] == "UNTIL":
                cond = res[1]
                i += 1
                body = []
                while i < len(lines) and lines[i].startswith("    "):
                    body.append(lines[i][4:])
                    i += 1
                while not eval(cond, {"__builtins__": {}}, self.variables):
                    r = self.execute_block(body)
                    if r is not None:
                        result = r
            elif isinstance(res, tuple) and res[0] == "GO":
                var_name, iterable = res[1], res[2]
                i += 1
                body = []
                while i < len(lines) and lines[i].startswith("    "):
                    body.append(lines[i][4:])
                    i += 1
                for val in iterable:
                    self.variables[var_name] = val
                    r = self.execute_block(body)
                    if r is not None:
                        result = r
            elif res == "EXEC_BLOCK":
                i += 1
                block = []
                while i < len(lines) and lines[i].startswith("    "):
                    block.append(lines[i][4:])
                    i += 1
                r = self.execute_block(block)
                if r is not None:
                    result = r
            else:
                if res is not None:
                    result = res
                i += 1
        return result

    def run(self, code):
        lines = code.split("\n")
        blocks = self.parse(lines)
        for content, block in blocks:
            if content.startswith("fnc "):
                fn_def = content[4:]
                fn_name, args_str = fn_def.split("(", 1)
                fn_name = fn_name.strip()
                params = args_str[:-1]
                param_list = [p.strip() for p in params.split(",") if p.strip()]
                self.functions[fn_name] = (param_list, block)
            else:
                self.execute_block([content] + ["    " + b for b in block])

def main():
    if len(sys.argv) < 2:
        print("Usage: pebble <file.pb>")
        return
    filename = sys.argv[1]
    with open(filename, "r", encoding="utf-8") as f:
        code = f.read()
    parser = PebbleParser()
    parser.run(code)

if __name__ == "__main__":
    main()
