#include <cs50.h>
#include <stdio.h>

int main(void)
{
    int Height;

    do
    {
        Height = get_int("Height: "); //Prompts user for designated height//
    }
    while (Height < 1 || Height > 8); //Only allows 1-8 height, otherwise repeats//


    for (int i = 0; i < Height; i++)
    {
        for (int j = 0; j < Height - i - 1; j++) //Apex at the top, decreases.//
        {
            printf(" ");
        }


        for (int j = 0; j < i + 1; j++)
        {
            printf("#");
        }

        printf("\n");
    }
}
