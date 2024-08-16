#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#define BLOCK_SIZE 512

int main(int argc, char *argv[])
{
    if (argc != 2) // Doesn't equal to 2
    {
        printf("Usage: ./recover IMAGE\n");
        return 1;
    }
    char *file = argv[1];
    FILE *raw_file = fopen(file, "r");
    if (raw_file == NULL)
    {
        printf("Couldn't Open %s. \n", file);
        return 1;
    }
    bool exist_jpg = false;
    int jpg_count = 0;
    uint8_t buffer[BLOCK_SIZE]; // Create a new type to store a byte of data
    char jpg_name[8];
    FILE *outpointer = NULL;
    while (fread(buffer, BLOCK_SIZE, 1, raw_file) == 1) // Read data from a file
    {
        if (buffer[0] == 0xff && buffer[1] == 0xd8 && buffer[2] == 0xff && (buffer[3] & 0xf0) == 0xe0)
        {
            if (exist_jpg)
            {
                fclose(outpointer);
            }
            exist_jpg = true;
            sprintf(jpg_name, "%03d.jpg", jpg_count); // Stores a formatted string at a location in memory.
            outpointer = fopen(jpg_name, "w");
            if (outpointer == NULL)
            {
                fclose(raw_file);
                printf("Couldn't create %s. \n", jpg_name);
                return 3;
            }
            jpg_count++;
        }
        if (exist_jpg)
        {
            fwrite(buffer, BLOCK_SIZE, 1, outpointer); // Writes data
        }
    }
    fclose(raw_file);
    if (exist_jpg)
    {
        fclose(outpointer);
    }
    return 0;
}