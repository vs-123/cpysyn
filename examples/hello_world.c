#include "stdio.h"
#include "math.h"
void main(int argc, char* argv[]) {
    printf("Hello, world!\n");
    int age = 27;
    if (age > 18) {
        printf("You are an adult!");
    } else {
        if (age > 12 && age < 18) {
            printf("You are a teenager!");
        } else {
            printf("You are younger than 12!");
        }
    }
}
