#include <cs50.h>
#include <stdio.h>

const int N = 3;
//"Const" is a global variable, used everywhere..."Int" making it called "N" whic his the number of scores to be averaged//
float average(int array[]);
//The word array can be any word//
int main(void)
{
    // Scores
    int scores[N];
    for (int i = 0; i < N; i++)
    {
        scores[i] = get_int("Average Score: ");
    }
    // Print average
    printf("Average: %f\n", average(scores));
}

float average(int array[])

{
    // Calculate average
    int sum = 0;
    for (int i = 0; i < N; i++)
    {
        sum += array[i];
    }
    return sum / (float) N;
}




//Score for %i: 59// (For 3 only)
//Score for %d: 59// (For 3 only)
//Score for %f: 59.333333// (For 3.0 only) (Decimal)