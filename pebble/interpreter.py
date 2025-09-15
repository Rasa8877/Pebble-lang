# interpreter.py

class ReturnValue(Exception):
    def __init__(self, value):
        self.value = value

class PebbleInterpreter:
    def __init__(self):
        self.vars = {}
        self.functions = {}

    def run(self, filename):
        with open(filename, "r", encoding="utf-8") as f:
            lines = f.readlines()
        self.execute_block(lines)

    def execute_block(self, lines):
        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Skip empty lines
            if not line:
                i += 1
                continue

            # Skip comments anywhere
            if line.startswith("!"):
                i += 1
                continue

            # Function definition
            if line.startswith("fnc "):
                i = self.handle_function(lines, i)
                continue

            # Loop: go
            if line.startswith("go "):
                i = self.handle_go(lines, i)
                continue

            # Loop: until
            if line.startswith("until "):
                i = self.handle_until(lines, i)
                continue

            # Other commands
            self.execute_line(line)
            i += 1

    # ----------------- Function Handling -----------------
    def handle_function(self, lines, index):
        header = lines[index].strip()
        fn_name = header.split()[1].split("(")[0]
        fn_lines = []
        index += 1

        while index < len(lines):
            line = lines[index].rstrip()
            if line.strip() == "":
                index += 1
                continue
            if line.startswith(" ") or line.startswith("\t"):
                fn_lines.append(line)
            else:
                break
            index += 1

        self.functions[fn_name] = fn_lines
        return index - 1

    # ----------------- Loops -----------------
    def handle_go(self, lines, index):
        header = lines[index].strip()
        var_name = header.split()[1]
        collection_str = header[header.find("{"):].strip()
        collection = self.evaluate(collection_str)
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
        header = lines[index].strip()
        condition_str = header[len("until "):]
        loop_lines = []
        index += 1
        while index < len(lines):
            line = lines[index]
            if line.startswith(" ") or line.startswith("\t"):
                loop_lines.append(line)
                index += 1
            else:
                break
        while self.evaluate(condition_str) == False:
            self.execute_block(loop_lines)
        return index - 1

    # ----------------- Execute Line -----------------
    def execute_line(self, line):
        line = line.strip()
        if not line:
            return

        # Function call
        if "(" in line and ")" in line:
            fn_name = line.split("(")[0]
            args_str = line[line.find("(")+1:line.find(")")]
            args = [self.evaluate(arg.strip()) for arg in args_str.split(",") if arg.strip()]
            if fn_name in self.functions:
                try:
                    # Store arguments as local vars
                    self.execute_block(self.functions[fn_name])
                except ReturnValue as rv:
                    return rv.value
            else:
                # maybe built-in function
                self.execute_builtin(fn_name, args)
            return

        # Variable assignment
        if " is " in line:
            var, expr = line.split(" is ", 1)
            self.vars[var.strip()] = self.evaluate(expr.strip())
            return

        # Say command
        if line.startswith("say "):
            print(self.evaluate(line[4:].strip()))
            return

        # Out command
        if line.startswith("out "):
            raise ReturnValue(self.evaluate(line[4:].strip()))

        raise Exception(f"Unknown command: {line}")

    # ----------------- Built-ins -----------------
    def execute_builtin(self, name, args):
        if name == "add":
            return sum(args)
        if name == "double":
            return args[0] * 2
        raise Exception(f"Unknown function: {name}")

    # ----------------- Evaluator -----------------
    def evaluate(self, expr):
        expr = expr.strip()
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
            if not content:
                return result
            for pair in content.split(","):
                key, val = pair.split(":")
                result[self.evaluate(key.strip())] = self.evaluate(val.strip())
            return result

        # Boolean values
        if expr == "True":
            return True
        if expr == "False":
            return False

        # Simple math
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

        return expr

# ----------------- Main -----------------
def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: pebble file.pb")
        return
    PebbleInterpreter().run(sys.argv[1])

if __name__ == "__main__":
    main()
