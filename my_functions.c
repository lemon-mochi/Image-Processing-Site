// my_functions.c
#include <stdio.h>
// For the saturate function, when I used numpy, the code was buggy, when I converted to pandas, it would fail with large images.
// I decided it would be easier to write this in C.
// I did not know how to deal with 2-d arrays, so I converted the numpy array to a 1-d array.
void saturate(int* array, int len, int channels) {
    for (int i = 0; i < len; i += channels) {
        int avg = (array[i] + array[i+1] + array[i+2]) / 3;
        array[i] = avg + 1.4 * (array[i] - avg);
        array[i+1] = avg + 1.4 * (array[i+1] - avg);
        array[i+2] = avg + 1.4 * (array[i+2] - avg);
        //ensure values are between 0 and 255
        if (array[i] < 0) array[i] = 0;
        if (array[i+1] < 0) array[i+1] = 0;
        if (array[i+2] < 0) array[i+2] = 0;
        if (array[i] > 255) array[i] = 255;
        if (array[i+1] > 255) array[i+1] = 255;
        if (array[i+2] > 255) array[i+2] = 255;
    }
}

// For the ordered dithering function, for some unknown reason, when I tried to use Numpy, I would
// sometimes get grey pixels in the final image. I would run tests such as counting the number of non
// 0 and 255 values and the function seems to be working properly but the images surely look wrong.
// I decided to write in C to test if this would fix the problem.
// This function expects the input array to be 1-dimensional
// After a test, I can see that this function does the exact same thing. I really do not know why some pixels 
// appear as grey. Maybe because of the greyscale thing is done in Python.
// Even when converting to greyscale in C instead of Python, the output still contains grey values.
// The problem must be something not caused by the code.
void ordered_dithering(int cols, unsigned char* inputArray, unsigned char* outputArray, int len, int channels) {
    // define the 4x4 Bayer matrix
    unsigned char bayer_matrix[4][4] = {
        {0, 8, 2, 10},
        {12, 4, 14, 6},
        {3, 11, 1, 9},
        {15, 7, 13, 5}
    };

    // x will keep track of which row the loop is on
    int x;
    // y will keep track of which column the loop is on
    int y;
    // o will keep track of which pixel to update in the outputArray
    int o = 0;
    for (int k = 0; k < len; k += channels) {
        // to find the row, divide by the index (k) by the number of rows
        x = (k / channels) / cols;
        // to find the column, find the remainder when dividing the index (k) by 
        // the number of columns
        y = (k / channels) % cols;

        // i and j are for the value of the Bayer matrix to compare to
        int i = x % 4;
        int j = y % 4;

        // divide by 15 to normalize the grey value
        unsigned char greyValue = (int) (0.299 * inputArray[k] + 0.587 * inputArray[k + 1] + 0.114 * inputArray[k + 2]) / 15;
        // perform the ordered dithering. If the normalized value is greater than the Bayer matrix's,
        // make it black, oterwise, make it white
        if (greyValue > bayer_matrix[i][j]) {
            outputArray[o] = 255;
        }
        o++;
    }

    for (int i = 0; i < o; i++) {
        if (outputArray[i] != 0 && outputArray[i] != 255) printf("%i\n", outputArray[i]);
    }
}