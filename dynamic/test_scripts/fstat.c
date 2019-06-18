#include <stdio.h> 
#include <sys/types.h> 
#include <sys/stat.h> 
#include <unistd.h> 
#include <errno.h> 
#include <string.h> 
#include <fcntl.h> 
 
int main(void) { 
	int f_d = 0; 
	struct stat st; 
	f_d = open("fstat.c",O_RDONLY); 
 
 	if(f_d == -1) { 
		printf("Error fd\n"); 
		return -1; 
	} 
 
	errno = 0; 
	if(fstat(f_d, &st)) { 
		printf("Error fstat\n"); 
		close(f_d); 
		return -1; 
	}  
	close(f_d); 
	return 0; 
}