


// gcc -o small_c_input small_c_input.c -static
#include <stdio.h>
int main( ) {
   int c;

//   printf( "a == :");
   c = getchar( );

//   printf( "\nb == : ");
 //  putchar( c );
   printf("%c\n", c);
   return 0;
}