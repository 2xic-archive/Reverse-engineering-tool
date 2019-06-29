# ported from https://github.com/qemu/qemu/blob/3e29da9fd81002a0c03041aaa26dea6d9dd9bd65/target/i386/hvf/x86_cpuid.c
'''
 *  i386 CPUID helper functions
 *
 *  Copyright (c) 2003 Fabrice Bellard
 *  Copyright (c) 2017 Google Inc.
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2 of the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with this program; if not, see <http://www.gnu.org/licenses/>.
 *
 * cpuid
'''

import triceforce_extender


CPUID_FP87 = (1 << 0)
CPUID_VME  = (1 << 1)
CPUID_DE   = (1 << 2)
CPUID_PSE  = (1 << 3)
CPUID_TSC  = (1 << 4)
CPUID_MSR  = (1 << 5)
CPUID_PAE  = (1 << 6)
CPUID_MCE  = (1 << 7)
CPUID_CX8  = (1 << 8)
CPUID_APIC = (1 << 9)
CPUID_SEP  = (1 << 11) # sysenter/sysexit 
CPUID_MTRR = (1 << 12)
CPUID_PGE  = (1 << 13)
CPUID_MCA  = (1 << 14)
CPUID_CMOV = (1 << 15)
CPUID_PAT  = (1 << 16)
CPUID_PSE36   = (1 << 17)
CPUID_PN   = (1 << 18)
CPUID_CLFLUSH = (1 << 19)
CPUID_DTS = (1 << 21)
CPUID_ACPI = (1 << 22)
CPUID_MMX  = (1 << 23)
CPUID_FXSR = (1 << 24)
CPUID_SSE  = (1 << 25)
CPUID_SSE2 = (1 << 26)
CPUID_SS = (1 << 27)
CPUID_HT = (1 << 28)
CPUID_TM = (1 << 29)
CPUID_IA64 = (1 << 30)
CPUID_PBE = (1 << 31)


CPUID_EXT_SSE3     = (1 << 0)
CPUID_EXT_PCLMULQDQ = (1 << 1)
CPUID_EXT_DTES64   = (1 << 2)
CPUID_EXT_MONITOR  = (1 << 3)
CPUID_EXT_DSCPL    = (1 << 4)
CPUID_EXT_VMX      = (1 << 5)
CPUID_EXT_SMX      = (1 << 6)
CPUID_EXT_EST      = (1 << 7)
CPUID_EXT_TM2      = (1 << 8)
CPUID_EXT_SSSE3    = (1 << 9)
CPUID_EXT_CID      = (1 << 10)
CPUID_EXT_FMA      = (1 << 12)
CPUID_EXT_CX16     = (1 << 13)
CPUID_EXT_XTPR     = (1 << 14)
CPUID_EXT_PDCM     = (1 << 15)
CPUID_EXT_PCID     = (1 << 17)
CPUID_EXT_DCA      = (1 << 18)
CPUID_EXT_SSE41    = (1 << 19)
CPUID_EXT_SSE42    = (1 << 20)
CPUID_EXT_X2APIC   = (1 << 21)
CPUID_EXT_MOVBE    = (1 << 22)
CPUID_EXT_POPCNT   = (1 << 23)
CPUID_EXT_TSC_DEADLINE_TIMER = (1 << 24)
CPUID_EXT_AES      = (1 << 25)
CPUID_EXT_XSAVE    = (1 << 26)
CPUID_EXT_OSXSAVE  = (1 << 27)
CPUID_EXT_AVX      = (1 << 28)
CPUID_EXT_F16C     = (1 << 29)
CPUID_EXT_RDRAND   = (1 << 30)
CPUID_EXT_HYPERVISOR  = (1 << 31)

CPUID_EXT2_FPU     = (1 << 0)
CPUID_EXT2_VME     = (1 << 1)
CPUID_EXT2_DE      = (1 << 2)
CPUID_EXT2_PSE     = (1 << 3)
CPUID_EXT2_TSC     = (1 << 4)
CPUID_EXT2_MSR     = (1 << 5)
CPUID_EXT2_PAE     = (1 << 6)
CPUID_EXT2_MCE     = (1 << 7)
CPUID_EXT2_CX8     = (1 << 8)
CPUID_EXT2_APIC    = (1 << 9)
CPUID_EXT2_SYSCALL = (1 << 11)
CPUID_EXT2_MTRR    = (1 << 12)
CPUID_EXT2_PGE     = (1 << 13)
CPUID_EXT2_MCA     = (1 << 14)
CPUID_EXT2_CMOV    = (1 << 15)
CPUID_EXT2_PAT     = (1 << 16)
CPUID_EXT2_PSE36   = (1 << 17)
CPUID_EXT2_MP      = (1 << 19)
CPUID_EXT2_NX      = (1 << 20)
CPUID_EXT2_MMXEXT  = (1 << 22)
CPUID_EXT2_MMX     = (1 << 23)
CPUID_EXT2_FXSR    = (1 << 24)
CPUID_EXT2_FFXSR   = (1 << 25)
CPUID_EXT2_PDPE1GB = (1 << 26)
CPUID_EXT2_RDTSCP  = (1 << 27)
CPUID_EXT2_LM      = (1 << 29)
CPUID_EXT2_3DNOWEXT = (1 << 30)
CPUID_EXT2_3DNOW   = (1 << 31)

# CPUID[8000_0001].EDX bits that are aliase of CPUID[1].EDX bits on AMD CPUs 
CPUID_EXT2_AMD_ALIASES = (CPUID_EXT2_FPU | CPUID_EXT2_VME | \
								CPUID_EXT2_DE | CPUID_EXT2_PSE | \
								CPUID_EXT2_TSC | CPUID_EXT2_MSR | \
								CPUID_EXT2_PAE | CPUID_EXT2_MCE | \
								CPUID_EXT2_CX8 | CPUID_EXT2_APIC | \
								CPUID_EXT2_MTRR | CPUID_EXT2_PGE | \
								CPUID_EXT2_MCA | CPUID_EXT2_CMOV | \
								CPUID_EXT2_PAT | CPUID_EXT2_PSE36 | \
								CPUID_EXT2_MMX | CPUID_EXT2_FXSR)

CPUID_EXT3_LAHF_LM = (1 << 0)
CPUID_EXT3_CMP_LEG = (1 << 1)
CPUID_EXT3_SVM     = (1 << 2)
CPUID_EXT3_EXTAPIC = (1 << 3)
CPUID_EXT3_CR8LEG  = (1 << 4)
CPUID_EXT3_ABM     = (1 << 5)
CPUID_EXT3_SSE4A   = (1 << 6)
CPUID_EXT3_MISALIGNSSE = (1 << 7)
CPUID_EXT3_3DNOWPREFETCH = (1 << 8)
CPUID_EXT3_OSVW    = (1 << 9)
CPUID_EXT3_IBS     = (1 << 10)
CPUID_EXT3_XOP     = (1 << 11)
CPUID_EXT3_SKINIT  = (1 << 12)
CPUID_EXT3_WDT     = (1 << 13)
CPUID_EXT3_LWP     = (1 << 15)
CPUID_EXT3_FMA4    = (1 << 16)
CPUID_EXT3_TCE     = (1 << 17)
CPUID_EXT3_NODEID  = (1 << 19)
CPUID_EXT3_TBM     = (1 << 21)
CPUID_EXT3_TOPOEXT = (1 << 22)
CPUID_EXT3_PERFCORE = (1 << 23)
CPUID_EXT3_PERFNB  = (1 << 24)

CPUID_SVM_NPT          = (1 << 0)
CPUID_SVM_LBRV         = (1 << 1)
CPUID_SVM_SVMLOCK      = (1 << 2)
CPUID_SVM_NRIPSAVE     = (1 << 3)
CPUID_SVM_TSCSCALE     = (1 << 4)
CPUID_SVM_VMCBCLEAN    = (1 << 5)
CPUID_SVM_FLUSHASID    = (1 << 6)
CPUID_SVM_DECODEASSIST = (1 << 7)
CPUID_SVM_PAUSEFILTER  = (1 << 10)
CPUID_SVM_PFTHRESHOLD  = (1 << 12)

CPUID_7_0_EBX_FSGSBASE = (1 << 0)
CPUID_7_0_EBX_BMI1     = (1 << 3)
CPUID_7_0_EBX_HLE      = (1 << 4)
CPUID_7_0_EBX_AVX2     = (1 << 5)
CPUID_7_0_EBX_SMEP     = (1 << 7)
CPUID_7_0_EBX_BMI2     = (1 << 8)
CPUID_7_0_EBX_ERMS     = (1 << 9)
CPUID_7_0_EBX_INVPCID  = (1 << 10)
CPUID_7_0_EBX_RTM      = (1 << 11)
CPUID_7_0_EBX_MPX      = (1 << 14)
CPUID_7_0_EBX_AVX512F  = (1 << 16) # /* AVX-512 Foundation */
CPUID_7_0_EBX_RDSEED   = (1 << 18)
CPUID_7_0_EBX_ADX      = (1 << 19)
CPUID_7_0_EBX_SMAP     = (1 << 20)
CPUID_7_0_EBX_PCOMMIT  = (1 << 22) # /* Persistent Commit */
CPUID_7_0_EBX_CLFLUSHOPT = (1 << 23) # /* Flush a Cache Line Optimized */
CPUID_7_0_EBX_CLWB     = (1 << 24) # /* Cache Line Write Back */
CPUID_7_0_EBX_AVX512PF = (1 << 26) # /* AVX-512 Prefetch */
CPUID_7_0_EBX_AVX512ER = (1 << 27) # /* AVX-512 Exponential and Reciprocal */
CPUID_7_0_EBX_AVX512CD = (1 << 28) # /* AVX-512 Conflict Detection */

CPUID_7_0_ECX_UMIP     = (1 << 2)
CPUID_7_0_ECX_PKU      = (1 << 3)
CPUID_7_0_ECX_OSPKE    = (1 << 4)
CPUID_7_0_ECX_RDPID    = (1 << 22)

CPUID_XSAVE_XSAVEOPT   = (1 << 0)
CPUID_XSAVE_XSAVEC     = (1 << 1)
CPUID_XSAVE_XGETBV1    = (1 << 2)
CPUID_XSAVE_XSAVES     = (1 << 3)

CPUID_6_EAX_ARAT       = (1 << 2)

#/* CPUID[0x80000007].EDX flags: */
CPUID_APM_INVTSC       = (1 << 8)

CPUID_VENDOR_SZ  =    12

CPUID_VENDOR_INTEL_1 = 0x756e6547 # /* "Genu" */
CPUID_VENDOR_INTEL_2 = 0x49656e69 # /* "ineI" */
CPUID_VENDOR_INTEL_3 = 0x6c65746e # /* "ntel" */
CPUID_VENDOR_INTEL = "GenuineIntel"

CPUID_VENDOR_AMD_1 =  0x68747541 # /* "Auth" */
CPUID_VENDOR_AMD_2 =  0x69746e65 # /* "enti" */
CPUID_VENDOR_AMD_3 =  0x444d4163 # /* "cAMD" */
CPUID_VENDOR_AMD =  "AuthenticAMD"

CPUID_VENDOR_VIA =  "CentaurHauls"

CPUID_MWAIT_IBE     = (1 << 1) /* Interrupts can exit capability */
CPUID_MWAIT_EMX     = (1 << 0) /* enumeration supported */


#	https://github.com/qemu/qemu/blob/68d7ff0cff0c4905802104843cf0100543b47314/target/i386/cpu.c
#	https://github.com/qemu/qemu/blob/3e29da9fd81002a0c03041aaa26dea6d9dd9bd65/target/i386/hvf/x86_cpuid.c


'''
	read wrong file, 
	should be porting from https://github.com/qemu/qemu/blob/68d7ff0cff0c4905802104843cf0100543b47314/target/i386/cpu.c
	void cpu_x86_cpuid(CPUX86State *env, uint32_t index, uint32_t count,
                   uint32_t *eax, uint32_t *ebx,
                   uint32_t *ecx, uint32_t *edx)
	-	alsooooo seems like 
'''

def run_cpuid(function, count, idx, unicorn):

	cpuid_response = triceforce_extender.run_cpuid(function, count)

	registers = [
		unicorn.reg_read(UC_X86_REG_EAX),
		unicorn.reg_read(UC_X86_REG_EBX),
		unicorn.reg_read(UC_X86_REG_ECX),
		unicorn.reg_read(UC_X86_REG_EDX)
	]

	for i in range(len(registers)):
		if(registers[i]):
			unicorn.reg_write(cpuid_response[i])
			break

	if(func == 0):
		if(registers[0] < 0xd):
#			unicorn.reg_write()
			pass
		else:
			unicorn.reg_write(UC_X86_REG_EAX, 0xd)

	elif(func == 1):
		edx = registers[3] & (CPUID_FP87 | CPUID_VME | CPUID_DE | CPUID_PSE | CPUID_TSC |
			 CPUID_MSR | CPUID_PAE | CPUID_MCE | CPUID_CX8 | CPUID_APIC |
			 CPUID_SEP | CPUID_MTRR | CPUID_PGE | CPUID_MCA | CPUID_CMOV |
			 CPUID_PAT | CPUID_PSE36 | CPUID_CLFLUSH | CPUID_MMX |
			 CPUID_FXSR | CPUID_SSE | CPUID_SSE2 | CPUID_SS)
		unicorn.reg_write(UC_X86_REG_EDX, edx)

		ecx = registers[2] & (CPUID_EXT_SSE3 | CPUID_EXT_PCLMULQDQ | CPUID_EXT_SSSE3 |
			 CPUID_EXT_FMA | CPUID_EXT_CX16 | CPUID_EXT_PCID |
			 CPUID_EXT_SSE41 | CPUID_EXT_SSE42 | CPUID_EXT_MOVBE |
			 CPUID_EXT_POPCNT | CPUID_EXT_AES | CPUID_EXT_XSAVE |
			 CPUID_EXT_AVX | CPUID_EXT_F16C | CPUID_EXT_RDRAND)
		ecx |= CPUID_EXT_HYPERVISOR

		unicorn.reg_write(UC_X86_REG_ECX, ecx)

	elif(func == 6):
		unicorn.reg_write(UC_X86_REG_EAX, CPUID_6_EAX_ARAT)
		unicorn.reg_write(UC_X86_REG_EBX, 0)
		unicorn.reg_write(UC_X86_REG_ECX, 0)
		unicorn.reg_write(UC_X86_REG_EDX, 0)


	elif(func == 7):
		if(idx == 0):
			ebx = registers[1] & (CPUID_7_0_EBX_FSGSBASE | CPUID_7_0_EBX_BMI1 |
					CPUID_7_0_EBX_HLE | CPUID_7_0_EBX_AVX2 |
					CPUID_7_0_EBX_SMEP | CPUID_7_0_EBX_BMI2 |
					CPUID_7_0_EBX_ERMS | CPUID_7_0_EBX_RTM |
					CPUID_7_0_EBX_RDSEED | CPUID_7_0_EBX_ADX |
					CPUID_7_0_EBX_SMAP | CPUID_7_0_EBX_AVX512IFMA |
					CPUID_7_0_EBX_AVX512F | CPUID_7_0_EBX_AVX512PF |
					CPUID_7_0_EBX_AVX512ER | CPUID_7_0_EBX_AVX512CD |
					CPUID_7_0_EBX_CLFLUSHOPT | CPUID_7_0_EBX_CLWB |
					CPUID_7_0_EBX_AVX512DQ | CPUID_7_0_EBX_SHA_NI |
					CPUID_7_0_EBX_AVX512BW | CPUID_7_0_EBX_AVX512VL |
					CPUID_7_0_EBX_INVPCID)

			raise Exception("hv_vmx_read_capability not implemented yet")
			'''
			hv_vmx_read_capability(HV_VMX_CAP_PROCBASED2, &cap);
			if (!(cap & CPU_BASED2_INVPCID)) {
				ebx &= ~CPUID_7_0_EBX_INVPCID;
			}

			ecx &= CPUID_7_0_ECX_AVX512BMI | CPUID_7_0_ECX_AVX512_VPOPCNTDQ;
			edx &= CPUID_7_0_EDX_AVX512_4VNNIW | CPUID_7_0_EDX_AVX512_4FMAPS;
			'''
		else:
		#	unicorn.reg_write(UC_X86_REG_EAX, CPUID_6_EAX_ARAT)
			unicorn.reg_write(UC_X86_REG_EBX, 0)
			unicorn.reg_write(UC_X86_REG_ECX, 0)
			unicorn.reg_write(UC_X86_REG_EDX, 0)
		unicorn.reg_write(UC_X86_REG_EAX, 0)

	elif(func == 0xD):
		'''
		if (idx == 0) {
			uint64_t host_xcr0 = xgetbv(0);
			uint64_t supp_xcr0 = host_xcr0 & (XSTATE_FP_MASK | XSTATE_SSE_MASK |
								  XSTATE_YMM_MASK | XSTATE_BNDREGS_MASK |
								  XSTATE_BNDCSR_MASK | XSTATE_OPMASK_MASK |
								  XSTATE_ZMM_Hi256_MASK | XSTATE_Hi16_ZMM_MASK);
			eax &= supp_xcr0;
		} else if (idx == 1) {
			hv_vmx_read_capability(HV_VMX_CAP_PROCBASED2, &cap);
			eax &= CPUID_XSAVE_XSAVEOPT | CPUID_XSAVE_XGETBV1;
			if (!(cap & CPU_BASED2_XSAVES_XRSTORS)) {
				eax &= ~CPUID_XSAVE_XSAVES;
			}
		}
		'''
		pass
	elif(func == 0x80000001):
		'''
		/* LM only if HVF in 64-bit mode */
		edx &= CPUID_FP87 | CPUID_VME | CPUID_DE | CPUID_PSE | CPUID_TSC |
				CPUID_MSR | CPUID_PAE | CPUID_MCE | CPUID_CX8 | CPUID_APIC |
				CPUID_EXT2_SYSCALL | CPUID_MTRR | CPUID_PGE | CPUID_MCA | CPUID_CMOV |
				CPUID_PAT | CPUID_PSE36 | CPUID_EXT2_MMXEXT | CPUID_MMX |
				CPUID_FXSR | CPUID_EXT2_FXSR | CPUID_EXT2_PDPE1GB | CPUID_EXT2_3DNOWEXT |
				CPUID_EXT2_3DNOW | CPUID_EXT2_LM | CPUID_EXT2_RDTSCP | CPUID_EXT2_NX;
		hv_vmx_read_capability(HV_VMX_CAP_PROCBASED, &cap);
		if (!(cap & CPU_BASED_TSC_OFFSET)) {
			edx &= ~CPUID_EXT2_RDTSCP;
		}
		ecx &= CPUID_EXT3_LAHF_LM | CPUID_EXT3_CMP_LEG | CPUID_EXT3_CR8LEG |
				CPUID_EXT3_ABM | CPUID_EXT3_SSE4A | CPUID_EXT3_MISALIGNSSE |
				CPUID_EXT3_3DNOWPREFETCH | CPUID_EXT3_OSVW | CPUID_EXT3_XOP |
				CPUID_EXT3_FMA4 | CPUID_EXT3_TBM;
		break;
		'''
		pass




