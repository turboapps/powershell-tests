// PROBE (VM-2932): list private memory regions of this process whose allocation starts with an MZ header,
// with each region's protection. Defender's Behavior:Win32/MZPEMemoryArtifacts.D flags executable private
// memory that holds a PE image no loader mapped; before the fix the VM's hand-mapped vm.dll was one
// PAGE_EXECUTE_READWRITE region. Prints a summary line: MZ_ALLOCS=<n> RWX_MZ_ALLOCS=<n> WX_REGIONS_IN_MZ=<n>.
#include <windows.h>
#include <stdio.h>
static const char* Prot(DWORD p) {
    switch (p & 0xFF) { case 0x01: return "NOACCESS"; case 0x02: return "R"; case 0x04: return "RW"; case 0x08: return "WC";
    case 0x10: return "X"; case 0x20: return "RX"; case 0x40: return "RWX"; case 0x80: return "WCX"; } return "?"; }
int main() {
    MEMORY_BASIC_INFORMATION mbi; BYTE* p = nullptr; int mz = 0, rwxmz = 0, wx = 0;
    PVOID curAlloc = nullptr; bool curIsMz = false; bool curHasRwx = false;
    while (VirtualQuery(p, &mbi, sizeof(mbi)) == sizeof(mbi)) {
        if (mbi.State == MEM_COMMIT && mbi.Type == MEM_PRIVATE) {
            if (mbi.AllocationBase != curAlloc) {
                if (curIsMz && curHasRwx) rwxmz++;
                curAlloc = mbi.AllocationBase; curIsMz = false; curHasRwx = false;
                MEMORY_BASIC_INFORMATION b; 
                if (VirtualQuery(curAlloc, &b, sizeof(b)) && b.State == MEM_COMMIT && !(b.Protect & (PAGE_NOACCESS | PAGE_GUARD))) {
                    __try { curIsMz = ((BYTE*)curAlloc)[0] == 'M' && ((BYTE*)curAlloc)[1] == 'Z'; } __except (1) {}
                }
                if (curIsMz) { mz++; printf("MZ alloc %p\n", curAlloc); }
            }
            if (curIsMz) {
                printf("  region %p size %8zx prot %s\n", mbi.BaseAddress, mbi.RegionSize, Prot(mbi.Protect));
                if ((mbi.Protect & 0xFF) == 0x40 || (mbi.Protect & 0xFF) == 0x80) { curHasRwx = true; wx++; }
            }
        }
        p = (BYTE*)mbi.BaseAddress + mbi.RegionSize;
    }
    if (curIsMz && curHasRwx) rwxmz++;
    printf("MZ_ALLOCS=%d RWX_MZ_ALLOCS=%d WX_REGIONS_IN_MZ=%d\n", mz, rwxmz, wx);
    return 0;
}
