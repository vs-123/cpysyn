import stdio, math

def main(argc: int, argv: list[str]):
    printf("Hello, world!\n")
    age: int = 27
    if age > 18:
        printf("You are an adult!")
    elif age > 12 and age < 18:
        printf("You are a teenager!")
    else:
        printf("You are younger than 12!")