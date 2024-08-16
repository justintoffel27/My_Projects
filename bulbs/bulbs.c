#include <cs50.h>
#include <stdio.h>
#include <string.h>

const int b = 8; // 8 Per Row//
void print_bulb(int bits);
int main(void)
{
    string input = get_string("Message: "); // User Input Message//
    for (int i = 0, n = strlen(input); i < n; i++)
    {
        char current_value = input[i];
        int ascii = (int) current_value;
        for (int j = b - 1; j >= 0; j--)
        {
            int bit = (ascii >> j) & 1;
            print_bulb(bit);
        }
        printf("\n");
    }
    printf("\n");
    return 0;
}
void print_bulb(int bits) // Takes integer bits as an input, 0 or 1//
{
    if (bits == 0) // Off//
    {
        printf("\U000026AB"); // Dark Bulb//
    }
    else if (bits == 1) // On//
    {
        printf("\U0001F7E1"); // Light Bulb//
    }
}
