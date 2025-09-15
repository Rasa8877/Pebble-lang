# Pebble Programming Language

Pebble is a beginner-friendly programming language built in Python.  
It’s designed to be simple, readable, and fun for learners and hobbyists.

---

## Features

- **Functions:** Define with `fnc` and return values with `out`
- **Loops:** `go` (for loops) and `until` (while loops)
- **Conditions:** `if`, with comparison keywords `big`, `sml`, `eql`, and boolean operators `and`, `or`, `not`
- **Collections:** Lists `{}` and dictionaries `[]` with easy syntax
- **Input:** `inp[...]` to get user input
- **Comments:** Use `!` to ignore text on a line
- **Error Handling:** `try-catch-finally` blocks for graceful error handling
- **Math:** `+`, `-`, `*`, `/`, `//`, `%`, `^`, and functions like `abs()`, `round()`, `sqrt()`, etc.
- **Utility Functions:** `len`, `range`, `keys`, `values`, `append`, `remove`, `contains`, `str`, `int`, `float`
- **Easy to run:** Execute `.pb` files with a single command

---

## Installation

```bash
pip install pebble-lang
````

---

## Usage

### Running a Pebble program

```bash
pebble examples/hello.pb
```

### Example Pebble program (`hello.pb`)

```pebble
say "Hello Pebble!"

x is 2 ^ 3
say x            ! Output: 8

nums is {1, 2, 3}
say len(nums)    ! Output: 3

fnc greet(name):
    say "Hello " + name

greet("Rasa")
```

---

## Loops and Conditions

```pebble
go i in 1 to 5:
    say i

x is 10
if x big 5:
    say "x is bigger than 5"
```

---

## Error Handling

```pebble
try:
    x is 5 / 0
catch e:
    say "Error: " + e
finally:
    say "Cleanup done"
```

---

## Collections

```pebble
numbers is {1, 2, 3}
numbers is append(numbers, 4)
say numbers        ! Output: [1, 2, 3, 4]

person is [name: "Rasa", age: 14]
say keys(person)   ! Output: ["name", "age"]
say values(person) ! Output: ["Rasa", 14]
```

---

## Input

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

Contributions are welcome! Please open issues or pull requests on the [GitHub repository](https://github.com/yourusername/pebble-lang).

---

## Contact

Created by Rasa8877
GitHub: [https://github.com/Rasa8877/pebble-lang](https://github.com/Rasa8877/pebble-lang)
