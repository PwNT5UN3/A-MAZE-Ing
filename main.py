from dataclasses import dataclass, fields

@dataclass
class test:
    foo: int = 1
    bar: int = 2

def main():
    tests = test()
    print(list(map(lambda x: x.name, fields(tests))))


if __name__ == "__main__":
    main()
