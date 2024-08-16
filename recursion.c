#include <cs50.h>
#include <stdio.h>

void draw(int n);

int main(void)
{
    // Get height of pyramid from prompted to user
    int height = get_int("Height: ");

    // Draws pyramid
    draw(height);
}

void draw(int n)
{
    // If there's nothing left to draw
    if (n <= 0)
    {
        return;
    }

    // Draw pyramid of height n - 1 from bottom to top
    draw(n - 1);

    // Draw one more row of width n
    for (int i = 0; i < n; i++) // Starts from bottom (0) and increases overtime from (i++)
    {
        printf("#"); // If something needs to be drawn, print "#"
    }
    printf("\n"); // Ensures there is no "$"
}