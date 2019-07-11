
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <sys/utsname.h>
#include <unistd.h>
#include <sys/types.h>

int main(void) {
	printf("%i\n", geteuid());
}