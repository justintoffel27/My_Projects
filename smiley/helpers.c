#include "helpers.h"

void colorize(int height, int width, RGBTRIPLE image[height][width])

{
    for (int i = 0; i < height; i++) // Describes each row (Height)
    {
        for (int j = 0; j < width; j++) // Describes each columns (Width)
        {                               // 0x00 are RGBS, changes pixels into RGB
            if (image[i][j].rgbtRed == 0x00 && image[i][j].rgbtGreen == 0x00 && image[i][j].rgbtBlue == 0x00)
            { // No pixels = Red
                image[i][j].rgbtRed = 0xff;
            }
        }
    }
}