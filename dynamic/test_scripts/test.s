



; nasm -f macho test.s -o test

section     .text
global      _start

start:
	vmovd xmm0, esi;
	movq xmm1, xmm0;
	