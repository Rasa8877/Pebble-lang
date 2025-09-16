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
- **Math:** `+`, `-`, `*`, `/`, `//`, `%`, `^`, and functions like `abs()`, `round()`, `sqrt()`, etc.
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
say x
! Output: 8

nums is {1, 2, 3}
say len(nums)
! Output: 3

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
