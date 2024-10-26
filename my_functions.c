// my_functions.c
// For the saturate function, when I used numpy, the code was buggy, when I converted to pandas, it would fail with large images.
// I decided it would be easier to write this in C.
// I did not know how to deal with 2-d arrays, so I converted the numpy array to a 1-d array.
void saturate(int* array, int len, int channels) {
    for (int i = 0; i < len; i+= channels) {
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