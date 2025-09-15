# interpreter.py

class ReturnValue(Exception):
    def __init__(self, value):
        self.value = value

class PebbleInterpreter:
    def __init__(self):
        self.vars = {}
        self.functions = {}

    def run(self, filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                lines = f.readlines()
            self.execute_block(lines)
        except Exception as e:
            print(f"[Pebble Error] {e}")

    def execute_block(self, lines):
        i = 0
        while i < len(lines):
            line = lines[i].rstrip()

            # Ignore empty lines or comments
            if not line or line.strip().startswith("!"):
                i += 1
                continue

            # Function definition
            if line.startswith("fnc "):
                i = self.handle_function(lines, i)
                continue

            # Loops
            if line.startswith("go "):
                i = self.handle_go(lines, i)
                continue
            if line.startswith("until "):
                i = self.handle_until(lines, i)
                continue

            # Execute other commands
            self.execute_line(line)
            i += 1

    # ----------------- Function Handling -----------------
    def handle_function(self, lines, index):
        header = lines[index].strip()
        fn_name = header.split()[1].split("(")[0]
        fn_lines = []
        index += 1
        while index < len(lines):
            line = lines[index]
            if line.startswith(" ") or line.startswith("\t"):
                fn_lines.append(line)
                index += 1
            else:
                break
        self.functions[fn_name] = fn_lines
        return index - 1

    # ----------------- Loops -----------------
    def handle_go(self, lines, index):
        header = lines[index].strip()
        parts = header.split()
        if len(parts) < 4 or parts[2] != "in":
            raise Exception(f"Invalid go syntax: {header}")
        var_name = parts[1]
        collection = self.evaluate(" ".join(parts[3:]))
        loop_lines = []
        index += 1
        while index < len(lines):
            line = lines[index]
            if line.startswith(" ") or line.startswith("\t"):
                loop_lines.append(line)
                index += 1
            else:
                break
        for item in collection:
            self.vars[var_name] = item
            self.execute_block(loop_lines)
        return index - 1

    def handle_until(self, lines, index):
        condition = lines[index].strip()[len("until "):]
        loop_lines = []
        index += 1
        while index < len(lines):
            line = lines[index]
            if line.startswith(" ") or line.startswith("\t"):
                loop_lines.append(line)
                index += 1
            else:
                break
        while not self.evaluate(condition):
            self.execute_block(loop_lines)
        return index - 1

    # ----------------- Execute Line -----------------
    def execute_line(self, line):
        line = line.strip()
        if not line:
            return

        # Say command
        if line.startswith("say "):
            print(self.evaluate(line[4:].strip()))
            return

        # Return / out
        if line.startswith("out "):
            raise ReturnValue(self.evaluate(line[4:].strip()))

        # Variable assignment
        if " is " in line:
            var, expr = line.split(" is ", 1)
            self.vars[var.strip()] = self.evaluate(expr.strip())
            return

        # Function call as statement
        if "(" in line and ")" in line:
            self.evaluate(line)
            return

        raise Exception(f"Unknown command: {line}")

    # ----------------- Evaluation -----------------
    def evaluate(self, expr):
        expr = expr.strip()

        # Function call inside expression
        if "(" in expr and ")" in expr:
            fn_name = expr.split("(")[0]
            args_str = expr[expr.find("(")+1:expr.find(")")]
            args = [self.evaluate(a.strip()) for a in args_str.split(",") if a.strip()]
            if fn_name in self.functions:
                # Save previous vars to avoid side effects
                saved_vars = self.vars.copy()
                try:
                    self.execute_block(self.functions[fn_name])
                except ReturnValue as rv:
                    self.vars = saved_vars
                    return rv.value
                self.vars = saved_vars
                return None
            else:
                return self.execute_builtin(fn_name, args)

        # Numbers
        try:
            if "." in expr:
                return float(expr)
            return int(expr)
        except ValueError:
            pass

        # Strings
        if expr.startswith('"') and expr.endswith('"'):
            return expr[1:-1]

        # Variables
        if expr in self.vars:
            return self.vars[expr]

        # Lists
        if expr.startswith("{") and expr.endswith("}"):
            content = expr[1:-1].strip()
            if not content:
                return []
            return [self.evaluate(x.strip()) for x in content.split(",")]

        # Dictionaries
        if expr.startswith("[") and expr.endswith("]"):
            content = expr[1:-1].strip()
            result = {}
            if content:
                for pair in content.split(","):
                    key, val = pair.split(":")
                    result[self.evaluate(key.strip())] = self.evaluate(val.strip())
            return result

        # Boolean constants
        if expr == "True":
            return True
        if expr == "False":
            return False

        # Boolean operators
        for op in [" and ", " or "]:
            if op in expr:
                a, b = expr.split(op)
                a = self.evaluate(a.strip())
                b = self.evaluate(b.strip())
                if op.strip() == "and": return a and b
                if op.strip() == "or": return a or b

        if expr.startswith("not "):
            return not self.evaluate(expr[4:].strip())

        # Comparisons
        if " big " in expr:
            a, b = expr.split(" big ")
            return self.evaluate(a.strip()) > self.evaluate(b.strip())
        if " sml " in expr:
            a, b = expr.split(" sml ")
            return self.evaluate(a.strip()) < self.evaluate(b.strip())
        if " eql " in expr:
            a, b = expr.split(" eql ")
            return self.evaluate(a.strip()) == self.evaluate(b.strip())

        # Math operators
        for op in ["+", "-", "*", "/", "//", "%", "^"]:
            if op in expr:
                a, b = expr.split(op)
                a = self.evaluate(a.strip())
                b = self.evaluate(b.strip())
                if op == "+": return a + b
                if op == "-": return a - b
                if op == "*": return a * b
                if op == "/": return a / b
                if op == "//": return a // b
                if op == "%": return a % b
                if op == "^": return a ** b

        # Fallback
        return expr

    # ----------------- Built-ins -----------------
    def execute_builtin(self, name, args):
        if name == "add":
            return sum(args)
        if name == "double":
            return args[0] * 2
        raise Exception(f"Unknown function: {name}")

# ----------------- Main -----------------
def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: pebble file.pb")
        return
    PebbleInterpreter().run(sys.argv[1])

if __name__ == "__main__":
    main()
