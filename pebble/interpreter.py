import sys


class ReturnValue(Exception):
    def __init__(self, value):
        self.value = value


def split_top_level(s, delimiter=','):
    """Split string by delimiter, ignoring delimiters inside quotes or brackets."""
    parts = []
    current = []
    in_quote = False
    quote_char = None
    depth = 0
    i = 0
    n = len(s)
    while i < n:
        ch = s[i]
        if in_quote:
            if ch == quote_char and s[i-1] != '\\':
                in_quote = False
                quote_char = None
            current.append(ch)
            i += 1
            continue
        if ch in '"\'':
            in_quote = True
            quote_char = ch
            current.append(ch)
            i += 1
            continue
        if ch in '([{':
            depth += 1
            current.append(ch)
            i += 1
            continue
        if ch in ')]}':
            depth -= 1
            current.append(ch)
            i += 1
            continue
        if ch == delimiter and depth == 0 and not in_quote:
            parts.append(''.join(current).strip())
            current = []
            i += 1
            continue
        current.append(ch)
        i += 1
    if current:
        parts.append(''.join(current).strip())
    return parts


class PebbleInterpreter:
    def __init__(self):
        self.variables = {}
        self.functions = {}
        self.builtins = {
            "say": self.execute_builtin,
            "inp": self.execute_builtin,
        }

    # ---------- Main execution ----------
    def run(self, filename):
        with open(filename, "r") as f:
            lines = f.readlines()
        try:
            self.execute_block(lines, indent_level=0)
        except ReturnValue as rv:
            print(rv.value)
        except Exception as e:
            print(f"[Pebble Error] {e}")

    def execute_block(self, lines, indent_level=0):
        i = 0
        while i < len(lines):
            raw_line = lines[i].rstrip("\n").replace("\t", "    ")
            line = raw_line.strip()
            if not line or line.startswith("$"):   # comments with $
                i += 1
                continue

            current_indent = len(raw_line) - len(raw_line.lstrip(" "))
            if current_indent < indent_level:
                return i

            consumed = self.execute_line(line, lines[i+1:], current_indent + 2, i+1)
            i += consumed + 1

    def execute_line(self, line, following_lines, next_indent_level, line_num):
        try:
            # ----- built-in statements -----
            if line.startswith("say "):
                args_str = line[4:].strip()
                values = self.evaluate_expression_list(args_str)
                print(*values)
                return 0

            if line.startswith("inp[") and line.endswith("]"):
                prompt = self.evaluate_expression(line[4:-1].strip())
                input(prompt)
                return 0

            if line.startswith("fnc "):
                name, rest = line[4:].split("(", 1)
                name = name.strip()
                params_str = rest.split(")")[0] if ")" in rest else ""
                params = [p.strip() for p in split_top_level(params_str) if p.strip()]
                body_start = self.find_block(following_lines, next_indent_level)
                body = following_lines[:body_start]
                self.functions[name] = (params, body)
                return body_start

            if line.startswith("out "):
                value = self.evaluate_expression(line[4:].strip())
                raise ReturnValue(value)

            # ----- if statement (fixed) -----
            if line.startswith("if "):
                # Check if it's an inline if with a statement after colon
                if ":" in line:
                    cond_part, rest = line[3:].split(":", 1)
                    cond_part = cond_part.strip()
                    rest = rest.strip()
                    if rest:
                        # Inline statement
                        if self.evaluate_condition(cond_part):
                            self.execute_line(rest, following_lines, next_indent_level, line_num)
                        return 0
                    else:
                        # Block if – condition is cond_part
                        cond = cond_part
                else:
                    cond = line[3:].strip()

                block_len = self.find_block(following_lines, next_indent_level)
                if self.evaluate_condition(cond):
                    block = following_lines[:block_len]
                    self.execute_block(block, next_indent_level)
                return block_len

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

            # ----- assignment -----
            if " is " in line:
                var, expr = line.split(" is ", 1)
                self.variables[var.strip()] = self.evaluate_expression(expr.strip())
                return 0

            # ----- function call (statement) -----
            if "(" in line and line.endswith(")"):
                fn_name, arg_str = line.split("(", 1)
                fn_name = fn_name.strip()
                arg_str = arg_str[:-1].strip()
                args = self.evaluate_expression_list(arg_str)
                if fn_name in self.functions:
                    self.call_function(fn_name, args)
                elif fn_name in self.builtins:
                    self.execute_builtin(fn_name, args)
                else:
                    raise Exception(f"Unknown function: {fn_name}")
                return 0

            return 0
        except Exception as e:
            raise Exception(f"Line {line_num}: {e}")

    # ---------- Expression evaluation ----------
    def evaluate_expression(self, expr):
        expr = expr.strip()
        if not expr:
            return None

        tokens = self.tokenize(expr)
        parser = self.ExpressionParser(self, tokens)
        result = parser.parse_expression()
        if parser.pos < len(tokens):
            raise Exception(f"Unexpected tokens after expression: {tokens[parser.pos:]}")
        return result

    def evaluate_expression_list(self, expr_str):
        if not expr_str.strip():
            return []
        parts = split_top_level(expr_str)
        return [self.evaluate_expression(p) for p in parts]

    def evaluate_condition(self, cond):
        return bool(self.evaluate_expression(cond))

    # ---------- Tokenizer ----------
    def tokenize(self, s):
        tokens = []
        i = 0
        n = len(s)
        while i < n:
            ch = s[i]
            if ch.isspace():
                i += 1
                continue

            # Numbers
            if ch.isdigit() or (ch == '.' and i+1 < n and s[i+1].isdigit()):
                num = ''
                while i < n and (s[i].isdigit() or s[i] == '.'):
                    num += s[i]
                    i += 1
                tokens.append(('NUMBER', num))
                continue

            # Strings
            if ch in '"\'':
                quote = ch
                i += 1
                string = ''
                while i < n and s[i] != quote:
                    if s[i] == '\\' and i+1 < n:
                        string += s[i+1]
                        i += 2
                    else:
                        string += s[i]
                        i += 1
                if i < n and s[i] == quote:
                    i += 1
                tokens.append(('STRING', string))
                continue

            # Identifiers (and operator aliases)
            if ch.isalpha() or ch == '_':
                ident = ''
                while i < n and (s[i].isalnum() or s[i] == '_'):
                    ident += s[i]
                    i += 1
                # Map operator aliases to real operators
                if ident == 'big':
                    tokens.append(('OP', '>'))
                elif ident == 'sml':
                    tokens.append(('OP', '<'))
                elif ident == 'eql':
                    tokens.append(('OP', '=='))
                else:
                    tokens.append(('IDENT', ident))
                continue

            # Single-character tokens: brackets, punctuation
            if ch in '{}[]():,':
                tokens.append((ch, ch))
                i += 1
                continue

            # Multi-character operators, including ^ -> ** and '!'
            if ch in '+-*/%^=!<>':
                op = ch
                i += 1
                # Handle multi-char operators
                if ch == '*' and i < n and s[i] == '*':
                    op = '**'
                    i += 1
                elif ch == '/' and i < n and s[i] == '/':
                    op = '//'
                    i += 1
                elif ch == '=' and i < n and s[i] == '=':
                    op = '=='
                    i += 1
                elif ch == '!' and i < n and s[i] == '=':
                    op = '!='
                    i += 1
                elif ch == '>' and i < n and s[i] == '=':
                    op = '>='
                    i += 1
                elif ch == '<' and i < n and s[i] == '=':
                    op = '<='
                    i += 1
                elif ch == '^':
                    op = '**'   # treat ^ as exponentiation
                tokens.append(('OP', op))
                continue

            raise Exception(f"Unexpected character: '{ch}'")
        return tokens

    # ---------- Expression parser ----------
    class ExpressionParser:
        def __init__(self, interpreter, tokens):
            self.interpreter = interpreter
            self.tokens = tokens
            self.pos = 0

        def peek(self):
            return self.tokens[self.pos] if self.pos < len(self.tokens) else None

        def consume(self):
            tok = self.peek()
            self.pos += 1
            return tok

        def expect(self, expected_type):
            tok = self.consume()
            if tok[0] != expected_type:
                raise Exception(f"Expected '{expected_type}', got {tok}")
            return tok

        def parse_expression(self):
            return self.parse_or()

        # ---------- Logical operators ----------
        def parse_or(self):
            left = self.parse_and()
            while self.peek() and self.peek()[0] == 'IDENT' and self.peek()[1] == 'or':
                self.consume()
                right = self.parse_and()
                left = left or right
            return left

        def parse_and(self):
            left = self.parse_not()
            while self.peek() and self.peek()[0] == 'IDENT' and self.peek()[1] == 'and':
                self.consume()
                right = self.parse_not()
                left = left and right
            return left

        def parse_not(self):
            if self.peek() and self.peek()[0] == 'IDENT' and self.peek()[1] == 'not':
                self.consume()
                return not self.parse_comparison()
            return self.parse_comparison()

        # ---------- Comparisons ----------
        def parse_comparison(self):
            left = self.parse_add_sub()
            tok = self.peek()
            while tok and tok[0] == 'OP' and tok[1] in ('>', '<', '==', '!=', '>=', '<='):
                self.consume()
                right = self.parse_add_sub()
                op = tok[1]
                if op == '>':
                    left = left > right
                elif op == '<':
                    left = left < right
                elif op == '==':
                    left = left == right
                elif op == '!=':
                    left = left != right
                elif op == '>=':
                    left = left >= right
                elif op == '<=':
                    left = left <= right
                tok = self.peek()
            return left

        # ---------- Arithmetic ----------
        def parse_add_sub(self):
            left = self.parse_mul_div()
            tok = self.peek()
            while tok and tok[0] == 'OP' and tok[1] in ('+', '-'):
                self.consume()
                right = self.parse_mul_div()
                if tok[1] == '+':
                    left += right
                else:
                    left -= right
                tok = self.peek()
            return left

        def parse_mul_div(self):
            left = self.parse_power()
            tok = self.peek()
            while tok and tok[0] == 'OP' and tok[1] in ('*', '/', '//', '%'):
                self.consume()
                right = self.parse_power()
                op = tok[1]
                if op == '*':
                    left *= right
                elif op == '/':
                    left /= right
                elif op == '//':
                    left //= right
                elif op == '%':
                    left %= right
                tok = self.peek()
            return left

        def parse_power(self):
            left = self.parse_unary()
            tok = self.peek()
            if tok and tok[0] == 'OP' and tok[1] == '**':
                self.consume()
                right = self.parse_unary()
                return left ** right
            return left

        def parse_unary(self):
            tok = self.peek()
            if tok and tok[0] == 'OP':
                if tok[1] == '-':
                    self.consume()
                    return -self.parse_unary()
                elif tok[1] == '!':   # logical NOT
                    self.consume()
                    return not self.parse_unary()
            return self.parse_primary()

        # ---------- Primary ----------
        def parse_primary(self):
            tok = self.peek()
            if not tok:
                raise Exception("Unexpected end of expression")

            value = None

            # Number
            if tok[0] == 'NUMBER':
                self.consume()
                value = float(tok[1]) if '.' in tok[1] else int(tok[1])

            # String
            elif tok[0] == 'STRING':
                self.consume()
                value = tok[1]

            # Identifier / variable / function call / built-in call
            elif tok[0] == 'IDENT':
                ident = tok[1]
                self.consume()
                if ident == 'true':
                    value = True
                elif ident == 'false':
                    value = False

                # Function call with parentheses
                elif self.peek() and self.peek()[0] == '(':
                    self.consume()  # '('
                    args = []
                    while self.peek() and self.peek()[0] != ')':
                        args.append(self.parse_expression())
                        if self.peek() and self.peek()[0] == ',':
                            self.consume()
                        else:
                            break
                    self.expect(')')
                    if ident in self.interpreter.functions:
                        value = self.interpreter.call_function(ident, args)
                    elif ident in self.interpreter.builtins:
                        value = self.interpreter.execute_builtin(ident, args)
                    else:
                        raise Exception(f"Unknown function: {ident}")

                # Built-in call with square brackets (e.g., inp[...])
                elif self.peek() and self.peek()[0] == '[' and ident in self.interpreter.builtins:
                    self.consume()  # '['
                    args = []
                    while self.peek() and self.peek()[0] != ']':
                        args.append(self.parse_expression())
                        if self.peek() and self.peek()[0] == ',':
                            self.consume()
                        else:
                            break
                    self.expect(']')
                    value = self.interpreter.execute_builtin(ident, args)

                else:
                    # Variable lookup
                    if ident in self.interpreter.variables:
                        value = self.interpreter.variables[ident]
                    else:
                        raise Exception(f"Undefined variable: {ident}")

            # Parenthesized expression
            elif tok[0] == '(':
                self.consume()
                value = self.parse_expression()
                self.expect(')')

            # List literal: { expr, expr, ... }
            elif tok[0] == '{':
                self.consume()
                items = []
                while self.peek() and self.peek()[0] != '}':
                    items.append(self.parse_expression())
                    if self.peek() and self.peek()[0] == ',':
                        self.consume()
                    else:
                        break
                self.expect('}')
                value = items

            # Dictionary literal: [ key: expr, key: expr, ... ]
            elif tok[0] == '[':
                self.consume()
                d = {}
                while self.peek() and self.peek()[0] != ']':
                    key_tok = self.peek()
                    if key_tok[0] not in ('IDENT', 'STRING'):
                        raise Exception(f"Invalid dictionary key: {key_tok}")
                    self.consume()
                    key = key_tok[1]  # always treat as string
                    self.expect(':')
                    d[key] = self.parse_expression()
                    if self.peek() and self.peek()[0] == ',':
                        self.consume()
                    else:
                        break
                self.expect(']')
                value = d

            else:
                raise Exception(f"Unexpected token: {tok}")

            # Handle postfix indexing: [expr] after any primary
            while self.peek() and self.peek()[0] == '[':
                self.consume()  # consume '['
                index = self.parse_expression()
                self.expect(']')
                # Perform indexing
                if isinstance(value, dict):
                    try:
                        value = value[index]
                    except KeyError:
                        raise Exception(f"Key '{index}' not found in dictionary")
                elif isinstance(value, list):
                    if not isinstance(index, int):
                        raise Exception(f"List index must be integer, got {type(index).__name__}")
                    try:
                        value = value[index]
                    except IndexError:
                        raise Exception(f"List index {index} out of range")
                elif isinstance(value, str):
                    if not isinstance(index, int):
                        raise Exception(f"String index must be integer, got {type(index).__name__}")
                    try:
                        value = value[index]
                    except IndexError:
                        raise Exception(f"String index {index} out of range")
                else:
                    raise Exception(f"Cannot index type {type(value).__name__}")

            return value

    # ---------- Functions ----------
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

    # ---------- Block detection ----------
    def find_block(self, lines, indent_level):
        for i, line in enumerate(lines):
            raw_line = line.replace("\t", "    ")
            if raw_line.strip() and (len(raw_line) - len(raw_line.lstrip(" "))) < indent_level:
                return i
        return len(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: pebble <file.peb>")
        sys.exit(1)
    PebbleInterpreter().run(sys.argv[1])


if __name__ == "__main__":
    main()