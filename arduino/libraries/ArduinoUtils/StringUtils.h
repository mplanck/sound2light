// A handful of generic functions to perform string manipulation.  These 
// functions are extremely limited right now to avoid bloating the stack
// memory on the arduino.  So if you want to expand capability, you'll need
// to up the maximum number of strings.

#ifndef _STRING_UTILS
#define _STRING_UTILS

#define MAX_NUM_STRINGS 4

// ------------------------------------------------------------------------
// UTILITIES

struct StringArray {
    String strings[MAX_NUM_STRINGS] ;
    int numStrings;
};

// Used to count the characters in the input that match the given
// char
int CountChars(String input, 
               char c)
{

    int returnValue = 0;
    int index = 0;

    while (index > -1) {
        index = input.indexOf(c, index);
        if(index > -1) {
          index+=1; // skip over the char we just accounted for
          returnValue+=1;
        }
    }

    return returnValue;
}

// Tokenize a string object into a StringArray struct.  This is limited to
// the maximum number of string objects a StringArray can contain.

StringArray StringTokenize(String input, char delimiter)
{

  int splitCount = 1 + min(MAX_NUM_STRINGS-1, CountChars(input, delimiter));

  StringArray output;
  output.numStrings = 0;

  int indexStart = 0;
  int indexEnd = -1;


  for(int i = 0; i < splitCount; i++) {
    indexEnd = input.indexOf(delimiter, indexStart);

    if(indexEnd < 0) indexEnd = input.length();

    output.strings[i] = input.substring(indexStart, indexEnd);

    indexStart = indexEnd+1; // skip over the delimiter

  }

  output.numStrings = splitCount;

  return output;

}
 

#endif