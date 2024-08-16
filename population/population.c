#include <cs50.h>
#include <stdio.h>

int main(void)
{
    // TODO: Prompt for start size
    int start_size;
    do
    {
        start_size = get_int("Start Size: ");
    }
    while (9 > start_size);
    // TODO: Prompt for end size
    int end_size;
    do
    {
        end_size = get_int("End Size: ");
    }
    while (start_size > end_size);
    // TODO: Calculate number of years until we reach threshold
    int years = 0;
    int current_population = start_size;

    while (current_population < end_size)
    {
        // Background Given //
        int births = current_population / 3;
        int deaths = current_population / 4;

        current_population = current_population + births - deaths;
        years++;
    }
    // TODO: Print number of years
    printf("Years: %i\n", years);
}
