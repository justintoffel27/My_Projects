#include <cs50.h>
#include <stdio.h>
#include <string.h>

int main(void)

{
    string name = get_string("What's your name? "); //Asking user for name//
    int n = strlen(name);
    printf("%i\n", n);
}


// int n = 0; //Initialize that n = 0//  while (name[n] != '\0') //!= means does not equal//   {      n++;    }    printf("%i\n", n);//






