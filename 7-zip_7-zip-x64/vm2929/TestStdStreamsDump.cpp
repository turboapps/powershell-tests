// TestStdStreamsDump - guest for BVTs.TestStdStreamsDump (VM-2929).
//
// Writes to standard output from several threads at once, the way Adobe's CC Libraries node.exe does, while
// the VM's standard stream dump (DumpStdStreams, which the turbo client always enables) copies everything
// written there into the session's xcstream log. Before the fix the dumper kept its pending text in one
// string per stream with no lock. One thread growing that string reallocated it while another was finding
// the next line break in it, the finder computed the line's length against the new buffer, and the negative
// size made std::vector throw std::length_error out of the WriteFile hook into the app.
//
// Each round runs in a fresh child process, because the dumper's string only reallocates when it grows past
// its largest size so far: a process gets one realloc per doubling of the longest pending text. In a round,
// one thread writes ever longer runs of text with no line break, each doubling the last, while the others
// write long lines. Standard output is a file, as node's was, so the volume does not go back to the test.
//
// The exit rounds instead end the process while the writers are still writing, so the exit kills threads in the
// middle of a dump; the VM's exit teardown flushes the dumper afterwards and must not wait on them.
//
// Usage:
//   TestStdStreamsDump.exe [exit] [rounds]   parent: runs the rounds (exit rounds with "exit"), one child each
//                                            (default 40)
//   TestStdStreamsDump.exe round             one round
//   TestStdStreamsDump.exe exitround         one exit round
//
// Parent exit code: 0 when every round exited 0, 1 when a round did not, 2 on a setup failure.

#include <windows.h>
#include <stdio.h>
#include <wchar.h>
#include <string>

namespace
{
    const int LineWriters = 7;
    const DWORD LineLength = 8 * 1024;
    const DWORD FirstRunLength = 4 * 1024;
    const DWORD LastRunLength = 1024 * 1024;

    volatile LONG g_growerDone = 0;

    bool WriteAll(HANDLE h, const char* data, DWORD length)
    {
        DWORD written = 0;
        return WriteFile(h, data, length, &written, nullptr) && written == length;
    }

    DWORD WINAPI LineWriter(LPVOID param)
    {
        // A different letter per thread, so the lines are not all the same text.
        std::string line(LineLength - 1, static_cast<char>('b' + reinterpret_cast<INT_PTR>(param)));
        line.push_back('\n');

        HANDLE hOut = GetStdHandle(STD_OUTPUT_HANDLE);
        while (InterlockedCompareExchange(&g_growerDone, 0, 0) == 0)
        {
            if (!WriteAll(hOut, line.data(), static_cast<DWORD>(line.size())))
            {
                return GetLastError();
            }
        }
        return 0;
    }

    DWORD WINAPI Grower(LPVOID)
    {
        std::string run(LastRunLength, 'a');

        HANDLE hOut = GetStdHandle(STD_OUTPUT_HANDLE);
        DWORD result = 0;
        for (DWORD length = FirstRunLength; length <= LastRunLength; length *= 2)
        {
            if (!WriteAll(hOut, run.data(), length))
            {
                result = GetLastError();
                break;
            }
            Sleep(1);
        }

        InterlockedExchange(&g_growerDone, 1);
        return result;
    }

    // Standard output becomes a file of our own. The VM recognises a write to standard output by comparing the
    // handle with GetStdHandle(STD_OUTPUT_HANDLE), so this file is what it dumps. Returns nullptr on failure.
    HANDLE RedirectStdoutToTempFile()
    {
        wchar_t tempDir[MAX_PATH];
        wchar_t tempFile[MAX_PATH];
        if (GetTempPathW(MAX_PATH, tempDir) == 0 || GetTempFileNameW(tempDir, L"ssd", 0, tempFile) == 0)
        {
            fwprintf(stderr, L"FAIL temp file name gle=%lu\n", GetLastError());
            return nullptr;
        }

        HANDLE hFile = CreateFileW(tempFile, GENERIC_WRITE, FILE_SHARE_READ | FILE_SHARE_DELETE, nullptr, CREATE_ALWAYS,
            FILE_ATTRIBUTE_TEMPORARY | FILE_FLAG_DELETE_ON_CLOSE, nullptr);
        if (hFile == INVALID_HANDLE_VALUE)
        {
            fwprintf(stderr, L"FAIL CreateFile gle=%lu\n", GetLastError());
            return nullptr;
        }
        SetStdHandle(STD_OUTPUT_HANDLE, hFile);
        return hFile;
    }

    // Exits the process while the line writers are still writing, so the exit kills threads in the middle of a
    // dump. The VM's exit teardown then flushes the dumper, and must not wait on a thread the exit killed.
    int RunExitRound()
    {
        if (RedirectStdoutToTempFile() == nullptr)
        {
            return 2;
        }

        for (int i = 0; i < LineWriters; i++)
        {
            if (CreateThread(nullptr, 0, LineWriter, reinterpret_cast<LPVOID>(static_cast<INT_PTR>(i)), 0, nullptr) == nullptr)
            {
                fwprintf(stderr, L"FAIL CreateThread gle=%lu\n", GetLastError());
                return 2;
            }
        }

        Sleep(200);
        ExitProcess(0);
    }

    int RunRound()
    {
        HANDLE hFile = RedirectStdoutToTempFile();
        if (hFile == nullptr)
        {
            return 2;
        }

        HANDLE threads[LineWriters + 1];
        for (int i = 0; i < LineWriters; i++)
        {
            threads[i] = CreateThread(nullptr, 0, LineWriter, reinterpret_cast<LPVOID>(static_cast<INT_PTR>(i)), 0, nullptr);
        }
        threads[LineWriters] = CreateThread(nullptr, 0, Grower, nullptr, 0, nullptr);
        for (HANDLE h : threads)
        {
            if (h == nullptr)
            {
                fwprintf(stderr, L"FAIL CreateThread gle=%lu\n", GetLastError());
                return 2;
            }
        }

        WaitForMultipleObjects(_countof(threads), threads, TRUE, INFINITE);

        int result = 0;
        for (HANDLE h : threads)
        {
            DWORD exitCode = 0;
            GetExitCodeThread(h, &exitCode);
            if (exitCode != 0)
            {
                fwprintf(stderr, L"FAIL a writer thread failed gle=%lu\n", exitCode);
                result = 2;
            }
            CloseHandle(h);
        }

        CloseHandle(hFile);
        return result;
    }
}

int wmain(int argc, wchar_t** argv)
{
    if (argc > 1 && _wcsicmp(argv[1], L"round") == 0)
    {
        return RunRound();
    }
    if (argc > 1 && _wcsicmp(argv[1], L"exitround") == 0)
    {
        return RunExitRound();
    }

    // Inherited by the rounds, so a round that crashes does not raise a WER dialog that would stall the run.
    SetErrorMode(SEM_FAILCRITICALERRORS | SEM_NOGPFAULTERRORBOX);

    int arg = 1;
    bool exitRounds = argc > arg && _wcsicmp(argv[arg], L"exit") == 0;
    if (exitRounds)
    {
        arg++;
    }
    int rounds = argc > arg ? _wtoi(argv[arg]) : 40;

    wchar_t selfPath[MAX_PATH];
    GetModuleFileNameW(nullptr, selfPath, MAX_PATH);

    wchar_t cmdLine[MAX_PATH + 16];
    swprintf_s(cmdLine, L"\"%s\" %s", selfPath, exitRounds ? L"exitround" : L"round");

    for (int round = 1; round <= rounds; round++)
    {
        STARTUPINFOW si = { sizeof(si) };
        PROCESS_INFORMATION pi = {};
        if (!CreateProcessW(selfPath, cmdLine, nullptr, nullptr, FALSE, 0, nullptr, nullptr, &si, &pi))
        {
            wprintf(L"FAIL CreateProcess gle=%lu\n", GetLastError());
            return 2;
        }

        WaitForSingleObject(pi.hProcess, INFINITE);
        DWORD exitCode = 0;
        GetExitCodeProcess(pi.hProcess, &exitCode);
        CloseHandle(pi.hThread);
        CloseHandle(pi.hProcess);

        if (exitCode != 0)
        {
            wprintf(L"round %d exit=0x%08lX\n", round, exitCode);
            fflush(stdout);
            return 1;
        }
    }

    wprintf(L"rounds=%d all exited 0\n", rounds);
    return 0;
}
