

def stat_mode(mode):
	#	based off https://elixir.bootlin.com/linux/v3.18/source/include/uapi/linux/stat.h#L8
	S_IFMT = 61440
	S_IFSOCK = 49152
	S_IFLNK	 = 40960
	S_IFREG = 32768
	S_IFBLK = 24576
	S_IFDIR = 16384
	S_IFCHR = 8192
	S_IFIFO = 4096
	S_ISUID = 2048
	S_ISGID = 1024
	S_ISVTX = 512

	S_ISLNK = lambda m:	(((m) & S_IFMT) == S_IFLNK)
	S_ISREG = lambda m:	(((m) & S_IFMT) == S_IFREG)
	S_ISDIR = lambda m:	(((m) & S_IFMT) == S_IFDIR)
	S_ISCHR = lambda m:	(((m) & S_IFMT) == S_IFCHR)
	S_ISBLK = lambda m:	(((m) & S_IFMT) == S_IFBLK)
	S_ISFIFO = lambda m:	(((m) & S_IFMT) == S_IFIFO)
	S_ISSOCK = lambda m:	(((m) & S_IFMT) == S_IFSOCK)

	print(S_ISLNK(mode))
	print(S_ISREG(mode))
	print(S_ISDIR(mode))

	print(S_ISCHR(mode))
	print(S_ISBLK(mode))
	print(S_ISFIFO(mode))
	print(S_ISSOCK(mode))

# why was it so hard to find macros for this...
# also I found it here https://github.com/a2o/lilo/blob/master/src/geometry.h 
# not logical at all

def parse_dev_id():
	MAJOR = lambda dev: ( ( (dev >> 8) & 0xfff) | ((dev >> 32) & ~0xfff))
	MINOR = lambda dev: ((dev & 0xff) | ((dev >> 12) & ~0xff))

	dev = 11 << 8
	print((MAJOR(dev), MINOR(dev)))

	# okay so we are reading
	#	sr0     11:0    1 1024M  0 rom 
	# based off lsblk? 

def parse_mode():
	#	mode_t    st_mode;    /* protection */

	
	#define S_IRWXU 0000700    /* RWX mask for owner */
	#define S_IRUSR 0000400    /* R for owner */
	#define S_IWUSR 0000200    /* W for owner */
	#define S_IXUSR 0000100    /* X for owner */

	#define S_IRWXG 0000070    /* RWX mask for group */
	#define S_IRGRP 0000040    /* R for group */
	#define S_IWGRP 0000020    /* W for group */
	#define S_IXGRP 0000010    /* X for group */

	#define S_IRWXO 0000007    /* RWX mask for other */
	#define S_IROTH 0000004    /* R for other */
	#define S_IWOTH 0000002    /* W for other */
	#define S_IXOTH 0000001    /* X for other */

	#define S_ISUID 0004000    /* set user id on execution */
	#define S_ISGID 0002000    /* set group id on execution */
	#define S_ISVTX 0001000    /* save swapped text even after use */
	pass






#MINOR = lambda (dev): (((dev) & 0xff) | ( ((dev) >> 12) & ~0xff))


'''
MKDEV = lambda (major,minor): (((minor & 0xff) | ((major & 0xfff) << 8) \
	  | (( (minor & ~0xff)) << 12) \
	  | (( (major & ~0xfff)) << 32)))
'''
