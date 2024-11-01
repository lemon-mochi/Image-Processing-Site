// my_functions.c
#include <stdio.h>
// For the saturate function, when I used numpy, the code was buggy, when I converted to pandas, it would fail with large images.
// I decided it would be easier to write this in C.
// I did not know how to deal with 2-d arrays, so I converted the numpy array to a 1-d array.
void saturate(short* array, int len, int channels) {
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
/*void ordered_dithering(
    int cols, unsigned char* inputArray, unsigned char* outputArray, int len, int channels
) {
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
}*/

// This blur function takes the average values of neighbouring pixels and sets that as the new value
// This function expects the input and output arrays to be the same size and shape 
// (1-dimensional 8-bit unsigned integers)
void blur(
    int rows, int cols, unsigned char* inputArray, unsigned char* outputArray, int len, int channels
) {
    // x will keep track of which row the loop is on
    int x;
    // y will keep track of which column the loop is on
    int y;

    int width = cols * channels;

    for (int i = 0; i < len; i += channels) {
        // There are nine cases, the four corners, pixels on the four edges, and then pixels in the middle of the image
        // to find the row, divide by the index (k) by the number of rows
        x = (i / channels) / cols;
        // to find the column, find the remainder when dividing the index (k) by 
        // the number of columns
        y = (i / channels) % cols;

        // dealing with top left pixel
        if (x == 0 && y == 0) {
            // need to consider pixel to right, pixel below, pixel on bottom right
            int bottomRightPixel = width + channels;
            outputArray[0] = (inputArray[channels] + inputArray[width] + inputArray[bottomRightPixel]) / 3;
            outputArray[1] = (inputArray[1 + channels] + inputArray[1 + width] + inputArray[1 + bottomRightPixel]) / 3;
            outputArray[2] = (inputArray[2 + channels] + inputArray[2 + width] + inputArray[2 + bottomRightPixel]) / 3;
        }

        // dealing with top right pixel
        else if (x == 0 && y == cols - 1) {
            // need to consider pixel to left, pixel below, and pixel on bottom left
            int leftPixel = i - channels;
            int bottomPixel = i + width;
            int bottomLeftPixel = bottomPixel - channels;
            outputArray[i] = (inputArray[leftPixel] + inputArray[bottomPixel] + inputArray[bottomLeftPixel]) / 3;
            outputArray[i + 1] = (inputArray[1 + leftPixel] + inputArray[1 + bottomPixel] + inputArray[1 + bottomLeftPixel]) / 3;
            outputArray[i + 2] = (inputArray[2 + leftPixel] + inputArray[2 + bottomPixel] + inputArray[2 + bottomLeftPixel]) / 3;
        }

        // dealing with bottom left pixel
        else if (x == rows - 1 && y == 0) {
            // need to consider pixel on right, pixel on top, pixel on top right
            int rightPixel = i + channels;
            int topPixel = i - width;
            int topRightPixel = topPixel + channels;
            outputArray[i] = (inputArray[rightPixel] + inputArray[topPixel] + inputArray[topRightPixel]) / 3;
            outputArray[i + 1] = (inputArray[1 + rightPixel] + inputArray[1 + topPixel] + inputArray[1 + topRightPixel]) / 3;
            outputArray[i + 2] = (inputArray[2 + rightPixel] + inputArray[2 + topPixel] + inputArray[2 + topRightPixel]) / 3;
        }

        // dealing with bottom right pixel
        else if (x == rows - 1 && y == cols - 1) {
            // need to consider pixel on left, pixel on top, pixel on top left
            int leftPixel = len - channels;
            int topPixel = len - width;
            int topLeftPixel = topPixel - channels;
            outputArray[i] = (inputArray[leftPixel] + inputArray[topPixel] + inputArray[topLeftPixel]) / 3;
            outputArray[i + 1] = (inputArray[1 + leftPixel] + inputArray[1 + topPixel] + inputArray[1 + topLeftPixel]) / 3;
            outputArray[i + 2] = (inputArray[2 + leftPixel] + inputArray[2 + topPixel] + inputArray[2 + topLeftPixel]) / 3;
        }

        // dealing with pixels on top row
        else if (x == 0) {
            // need to consider pixel to left, right, bottom left, bottom, and bottom right
            int leftPixel = i - channels;
            int rightPixel = i + channels;
            int bottomPixel = i + width;
            int bottomLeftPixel = leftPixel + width;
            int bottomRigthPixel = rightPixel + width;
            
            outputArray[i] = (
                inputArray[leftPixel] + inputArray[rightPixel] + inputArray[bottomPixel] + inputArray[bottomLeftPixel] + inputArray[bottomRigthPixel]
            ) / 5;

            outputArray[i + 1] = (
                inputArray[1 + leftPixel] + inputArray[1 + rightPixel] + inputArray[1 + bottomPixel] + inputArray[1 + bottomLeftPixel] + inputArray[1 + bottomRigthPixel]
            ) / 5;

            outputArray[i + 2] = (
                inputArray[2 + leftPixel] + inputArray[2 + rightPixel] + inputArray[2 + bottomPixel] + inputArray[2 + bottomLeftPixel] + inputArray[2 + bottomRigthPixel]
            ) / 5;
        }

        // dealing with pixels on bottom row
        else if (x == rows - 1) {
            // need to consider pixel on left, right, top, top left, top right
            int leftPixel = i - channels;
            int rightPixel = i + channels;
            int topPixel = i - width;
            int topLeftPixel = leftPixel - width;
            int topRightPixel = rightPixel - width;

            outputArray[i] = (
                inputArray[leftPixel] + inputArray[rightPixel] + inputArray[topPixel] + inputArray[topLeftPixel] + inputArray[topRightPixel]
            ) / 5;

            outputArray[i + 1] = (
                inputArray[1 + leftPixel] + inputArray[1 + rightPixel] + inputArray[1 + topPixel] + inputArray[1 + topLeftPixel] + inputArray[1 + topRightPixel]
            ) / 5;

            outputArray[i + 2] = (
                inputArray[2 + leftPixel] + inputArray[2 + rightPixel] + inputArray[2 + topPixel] + inputArray[2 + topLeftPixel] + inputArray[2 + topRightPixel]
            ) / 5;         
        }

        // dealing with pixels on left column
        else if (y == 0) {
            // need to consider pixel on top, botom, right, top right, bottom right
            int topPixel = i - width;
            int bottomPixel = i + width;
            int rightPixel = i + channels;
            int topRightPixel = rightPixel - width;
            int bottomRightPIxel = bottomPixel + channels;

            outputArray[i] = (
                inputArray[topPixel] + inputArray[topRightPixel] + inputArray[rightPixel] + inputArray[bottomPixel] + inputArray[bottomRightPIxel] 
            ) / 5;

            outputArray[i + 1] = (
                inputArray[1 + topPixel] + inputArray[1 + topRightPixel] + inputArray[1 + rightPixel] + inputArray[1 + bottomPixel] + inputArray[1 + bottomRightPIxel] 
            ) / 5;

            outputArray[i + 2] = (
                inputArray[2 + topPixel] + inputArray[2 + topRightPixel] + inputArray[2 + rightPixel] + inputArray[2 + bottomPixel] + inputArray[2 + bottomRightPIxel] 
            ) / 5;
        }

        // dealing with pixels on right column
        else if (y == cols - 1) {
            // need to consider pixel on top, bottom, left, top left, bottom left
            int topPixel = i - width;
            int topLeftPixel = topPixel - channels;
            int leftPixel = i - channels;
            int bottomPixel = i + width;
            int bottomLeftPixel = bottomPixel - channels;

            outputArray[i] = (
                inputArray[topLeftPixel] + inputArray[topPixel] + inputArray[leftPixel] + inputArray[bottomLeftPixel] + inputArray[bottomPixel]
            ) / 5;

            outputArray[i + 1] = (
                inputArray[1 + topLeftPixel] + inputArray[1 + topPixel] + inputArray[1 + leftPixel] + inputArray[1 + bottomLeftPixel] + inputArray[1 + bottomPixel]
            ) / 5;

            outputArray[i + 2] = (
                inputArray[2 + topLeftPixel] + inputArray[2 + topPixel] + inputArray[2 + leftPixel] + inputArray[2 + bottomLeftPixel] + inputArray[2 + bottomPixel]
            ) / 5;                                    
        }

        // pixels that are not in the corner or any edges
        else {
            // need to consider all eight adjacent pixels
            int leftPixel = i - channels;
            int rightPixel = i + channels;
            int topPixel = i - width;
            int bottomPixel = i + width;
            int topLeftPixel = topPixel - channels;
            int topRightPixel = topPixel + channels;
            int bottomLeftPixel = bottomPixel - channels;
            int bottomRightPixel = bottomPixel + channels;

            outputArray[i] = (
                inputArray[topLeftPixel] + inputArray[topPixel] + inputArray[topRightPixel] +
                inputArray[leftPixel] + inputArray[rightPixel] + 
                inputArray[bottomLeftPixel] + inputArray[bottomPixel] + inputArray[bottomRightPixel]
            ) / 8;

            outputArray[i + 1] = (
                inputArray[1 + topLeftPixel] + inputArray[1 + topPixel] + inputArray[1 + topRightPixel] +
                inputArray[1 + leftPixel] + inputArray[1 + rightPixel] + 
                inputArray[1 + bottomLeftPixel] + inputArray[1 + bottomPixel] + inputArray[1 + bottomRightPixel]
            ) / 8;

            outputArray[i + 2] = (
                inputArray[2 + topLeftPixel] + inputArray[2 + topPixel] + inputArray[2 + topRightPixel] +
                inputArray[2 + leftPixel] + inputArray[2 + rightPixel] + 
                inputArray[2 + bottomLeftPixel] + inputArray[2 + bottomPixel] + inputArray[2 + bottomRightPixel]
            ) / 8;
        }
        
        // for alpha channels, keep it as is
        if (channels == 4) {
            outputArray[i + 3] = inputArray[i + 3];
        }
    }
}

// This function is used to blur images which are in the greyscale format.
// Very similar to previous function.
void blurGrey(int rows, int cols, unsigned char* inputArray, unsigned char* outputArray, int len) {
    // x will keep track of which row the loop is on
    int x;
    // y will keep track of which column the loop is on
    int y;

    for (int i = 0; i < len; i++) {
        // find the x and y values
        x = i / cols;
        y = i % cols;

        // top left corner
        if (x == 0 && y == 0) {
            int bottomRightPixel = cols + 1;
            outputArray[0] = (inputArray[1] + inputArray[cols] + inputArray[bottomRightPixel]) / 3;
        }

        // top right corner
        else if (x == 0 && y == cols - 1) {
            int bottomPixel = i + cols;
            int bottomRightPixel = bottomPixel - 1;
            outputArray[i] = (inputArray[i - 1] + inputArray[bottomPixel] + inputArray[bottomRightPixel]) / 3;
        }

        // bottom left corner
        else if (x == rows -1 && y == 0) {
            int topPixel = i - cols;
            int topRightPixel = topPixel + 1;
            outputArray[i] = (inputArray[i + 1] + inputArray[topPixel] + inputArray[topRightPixel]) / 3;
        }

        // bottom right corner
        else if (x == rows - 1 && y == cols - 1) {
            int topPixel = i - cols;
            int topLeftPixel = topPixel - 1;
            outputArray[i] = (inputArray[i - 1] + inputArray[topPixel] + inputArray[topLeftPixel]) / 3;
        }

        // on top row
        else if (x == 0) {
            int leftPixel = i - 1;
            int rightPixel = i + 1;
            int bottomPixel = i + cols;
            int bottomLeftPixel = bottomPixel - 1;
            int bottomRightPixel = bottomPixel + 1;

            outputArray[i] = (
                inputArray[leftPixel] + inputArray[rightPixel] + inputArray[bottomLeftPixel] + inputArray[bottomPixel] + inputArray[bottomRightPixel]
            ) / 5;
        }

        // on bottom row
        else if (x == rows - 1) {
            int leftPixel = i - 1;
            int rightPixel = i + 1;
            int topPixel = i - cols;
            int topLeftPixel = topPixel - 1;
            int topRightPixel = topPixel + 1;

            outputArray[i] = (
                inputArray[topLeftPixel] + inputArray[topPixel] + inputArray[topRightPixel] + inputArray[leftPixel] + inputArray[rightPixel]
            ) / 5;
        }

        // on left column
        else if (y == 0) {
            int rightPixel = i + 1;
            int topPixel = i - cols;
            int bottomPixel = i + cols;
            int topRightPixel = topPixel + 1;
            int bottomRightPixel = bottomPixel + 1;

            outputArray[i] = (
                inputArray[topPixel] + inputArray[topRightPixel] + inputArray[rightPixel] + inputArray[bottomPixel] + inputArray[bottomRightPixel]
            ) / 5;
        }

        // on right column
        else if (y == cols - 1) {
            int leftPixel = i - 1;
            int topPixel = i - cols;
            int topLeftPixel = topPixel - 1;
            int bottomPixel = i + cols;
            int bottomLeftPixel = bottomPixel - 1;

            outputArray[i] = (
                inputArray[topLeftPixel] + inputArray[topPixel] + inputArray[leftPixel] + inputArray[bottomLeftPixel] + inputArray[bottomPixel]
            ) / 5;
        }

        else {
            int leftPixel = i - 1;
            int rightPixel = i + 1;
            int topPixel = i - cols;
            int bottomPixel = i + cols;
            int topLeftPixel = topPixel - 1;
            int topRightPixel = topPixel + 1;
            int bottomLeftPixel = bottomPixel - 1;
            int bottomRightPixel = bottomPixel + 1;

            outputArray[i] = (
                inputArray[topLeftPixel] + inputArray[topPixel] + inputArray[topRightPixel] + 
                inputArray[leftPixel] + inputArray[rightPixel] + 
                inputArray[bottomLeftPixel] + inputArray[bottomPixel] + inputArray[bottomRightPixel]
            ) / 8;
        }
    }
}