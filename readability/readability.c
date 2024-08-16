#include <cs50.h>
#include <ctype.h>
#include <math.h>
#include <stdio.h>
#include <string.h>

//----------------//
int count_letters(string text)

{
    int letters = 0;
    for (int i = 0, n = strlen(text); i < n; i++)
    {
        char c = text[i];
        if ((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z')) // Each letters (Upper and lowercase) increases letter count//
        {
            letters++;
        }
    }
    return letters;
}
//----------------//
int count_words(string text)

{
    int words = 1;
    for (int i = 0, n = strlen(text); i < n; i++)
    {
        char c = text[i];
        if (c == ' ' || c == '\t' || c == '\n') // Spaces, tab, and \n increases word count//
        {
            words++;
        }
    }
    return words;
}
//----------------//
int count_sentences(string text)

{
    int sentences = 0;
    for (int i = 0, n = strlen(text); i < n; i++)
    {
        char c = text[i];
        if (c == '.' || c == '!' || c == '?') // Each Sentence Enders increases sentences count//
        {
            sentences++;
        }
    }
    return sentences;
}
//----------------//
int main(void) // Start of program//

{
    string text = get_string("Text: ");
    int letters = count_letters(text);
    int words = count_words(text);
    int sentences = count_sentences(text);

    float L = (float) letters / words * 100;
    float S = (float) sentences / words * 100;
    int index = (int) round(0.0588 * L - 0.296 * S - 15.8); // Coleman-Liau Index//

    if (index < 1)
    {
        printf("Before Grade 1\n"); // (-)1//
    }
    else if (index >= 16)
    {
        printf("Grade 16+\n"); // (+)16//
    }
    else
    {
        printf("Grade %i\n", index); // 1-16//
    }
    return 0;
}
