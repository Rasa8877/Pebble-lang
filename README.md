# Pebble Programming Language

**Version 3.6.0**  
Pebble is a beginner‑friendly programming language built in Python.  
It’s designed to be simple, readable, and fun for learners and hobbyists.

---

## Features

- **Functions:** Define with `fnc` and return values with `out`
- **Loops:** `go` (for loops) and `until` (while loops)
- **Conditions:** `if` with comparison keywords `big`, `sml`, `eql`, and logical operators `and`, `or`, `not`, `!`
- **Collections:** Lists `{}` and dictionaries `[]` with easy syntax
- **Input:** `inp[...]` to get user input, and `num(...)` to convert input to numbers
- **Comments:** `$` at the start of a line (comments are ignored)
- **Math:** `+`, `-`, `*`, `/`, `//`, `%`, `^` (exponentiation)
- **Easy to run:** Execute `.peb` files with a single command

---

## Usage

### Running a Pebble program

```bash
python pebble/interpreter.py examples/hello.peb
```

### Example Pebble program (`hello.peb`)

```pebble
$ Hello Pebble! - Basic features demo
say "Hello Pebble!"

x is 2 ^ 3
say x
$ Output: 8

nums is {1, 2, 3}
count is 0
go n in nums:
    count is count + 1
say count
$ Output: 3

fnc greet(name):
    say "Hello " + name

greet("Rasa")
```

---

## Loops and Conditions

```pebble
nums is {0, 1, 2}
go i in nums:
    say "Hello"

x is 10
if x big 5:
    say "x is bigger than 5"
```

---

## WAWE – Why Add When Else Exists

Pebble does **not** have a separate `else` keyword – and it doesn’t need one!  
You can achieve the same effect by writing a second `if` that checks the opposite condition.

Example:

```pebble
x is 5

if x big 2:      $ true  (5 > 2)
    say "Hello"

if x sml 4:      $ false (5 < 4)
    say "Goodbye"
```

The second `if` only runs if `x sml 4` is true, which is the opposite of `x big 2` – exactly like an `else`.

You can chain multiple conditions by stacking `if`s – no need for `elif` or `else`!

---

## Logical Operators

Pebble supports `and`, `or`, `not` and also `!` for negation.  
Example:

```pebble
score is 75

if score big 80 and score sml 90:
    say "Grade B"
if score big 70 and score sml 80:
    say "Grade C"

if !true:
    say "This will not print"
if !false:
    say "This will print"
```

---

## Numbers from Input

The `inp[...]` function returns a **string**. To do arithmetic with user input, use the `num(...)` built‑in to convert it to a number (integer or float).  
Example – a simple calculator:

```pebble
$ Calculator with num()
a is num(inp["First number: "])
b is num(inp["Second number: "])
op is inp["Operator (+, -, *, /): "]

if op eql "+":
    say a + b
if op eql "-":
    say a - b
if op eql "*":
    say a * b
if op eql "/":
    if b eql 0:
        say "Cannot divide by zero"
    if ! (b eql 0):
        say a / b
```

If you enter `5`, `2`, `+`, the output will be `7` – not `52`!

---

## Collections

```pebble
numbers is {10, 20, 30}
say numbers

person is [name: "Rasa", age: 14]
say person

go n in numbers:
    say n * 2

say person["name"]
say person["age"]
```

This will output:

```
[10, 20, 30]
{'name': 'Rasa', 'age': 14}
20
40
60
Rasa
14
```

---

## Input (Text Only)

For plain text input (without conversion), you can still use `inp` directly:

```pebble
name is inp["Enter your name: "]
say "Hello " + name
```

---

## License

MIT License  
See [LICENSE](LICENSE) for details.

---

## Contributing

Contributions are welcome! Please open issues or pull requests on the [GitHub repository](https://github.com/Rasa8877/pebble-lang).

---

## Contact

Created by Rasa8877  
GitHub: [https://github.com/Rasa8877/pebble-lang](https://github.com/Rasa8877/pebble-lang)
