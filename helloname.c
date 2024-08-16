#include <cs50.h>
#include <stdio.h>

int main(void)
{
    string answer = get_string("What's your first name? ");
    printf("hello, %s\n", answer); //%s is "plug in some value here// //the two white "answer", in line 7, will go back to line 6 and plug into that %s//
} //Percentage symbols requires two symbols, such as "%%"//

