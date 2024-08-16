#include <cs50.h>
#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(void)
{
    // Get a string
    char *s = get_string("s: "); // Asks user for what value of 's' they want
    if (s == NULL) // If s = 0 or too much memory used...
    {
        return 1; // Return error and restart
    }
// --------------------------------------------------------------------------------
    // Allocate memory for another string
    char *t = malloc(strlen(s) + 1); // Grabs 's', uses malloc to allocate memory for another string (char array 't')
    if (t == NULL)                      // so theres enough space to hold 's' (Uses 'strlen' to count number of characters)
    {                                       // and '\0' (null (+1))
        return 1;
    }
// --------------------------------------------------------------------------------
    // Copy string into memory
    strcpy(t, s);

    // Capitalize copy
    if (strlen(t) > 0)
    {
        t[0] = toupper(t[0]); // Capitalizes first letter of 't' if it's not empty/null
    }

    // Print strings
    printf("s: %s\n", s);
    printf("t: %s\n", t);

    // Free memory of 't'
    free(t);
    return 0;
}
