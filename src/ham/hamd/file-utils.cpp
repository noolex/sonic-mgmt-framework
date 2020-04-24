#include <sys/types.h>
#include <sys/stat.h>
#include <dirent.h>             // opendir(), readdir()
#include <unistd.h>             // stat()
#include <glib.h>               // g_file_test(), etc...
#include <syslog.h>             // syslog(), LOG_WARNING
#include <limits.h>             // LINE_MAX

#include <algorithm>            // std::sort()
#include <vector>               // std::vector
#include <string>               // std::string
#include <map>                  // std::map

#include "file-utils.h"         // is_regular_file(), sorted_filelist()
#include "../shared/utils.h"    // startswith(), streq()

/**
 * @brief Return an ASCII-sorted vector of filename entries in a given
 *        directory. If no path is specified, the current working directory
 *        is used.
 *
 * @param dir_path_p Oath to the directory
 *
 * @return Sorted vector containing the list of files. Always check the
 *         value of the global @errno variable after using this function to
 *         see if anything went wrong. (It will be zero if all is well.)
 */
std::vector<std::string> sorted_filelist(const path_t & dir_path_r)
{
    std::vector<std::string> result;
    DIR    * dp;
    errno = 0;
    dp = opendir(dir_path_r.empty() ? "." : dir_path_r.c_str());
    if (dp)
    {
        dirent * de;
        while (true)
        {
            errno = 0;
            de = readdir(dp);
            if (de == NULL) break;

            path_t fullname = dir_path_r / de->d_name;

            if (g_file_test(fullname.c_str(), G_FILE_TEST_IS_REGULAR)) // Only keep regular files
                result.push_back(fullname);
        }
        closedir(dp);
        std::sort(result.begin(), result.end());
    }
    return result;
}

/**
 * @brief The group mapping file contains a mapping of roles and/or
 *        privilege-levels to Linux groups. Here are a few an examples:
 *
 *          ​sysadmin:sudo,adm,sys
 *          15:sudo,adm,sys
 *          secadmin:adm
 *          netoperator:operator
 *          0:operator​
 *
 *        This function reads the file and extracts the group mapping.
 *
 * @param fname_r Name of the file containing the group mapping.
 *
 * @return The group mapping as a std::map with the keys being the roles
 *         and/or privilege-levels and the values being a list (i.e.
 *         vector) of the Linux groups.
 */
std::map<std::string/*role*/, std::vector<std::string>/*groups*/> read_group_mapping(const path_t & fname_r)
{
    std::map<std::string/*role*/, std::vector<std::string>/*groups*/> group_mapping;

    FILE * file = fopen(fname_r.c_str(), "re");
    if (file)
    {
        #define WHITESPACE " \t\n\r"
        char    line[LINE_MAX];
        size_t  lineno = 0;
        char  * p;
        char  * s;
        char  * role;
        char  * groups; // comma-separated groups
        while (nullptr != (p = fgets(line, sizeof line, file)))
        {
            lineno++;

            p += strspn(p, WHITESPACE);            // Remove leading newline and spaces
            if (*p == '#' || *p == '\0') continue; // Skip comments and empty lines

            // Delete trailing comments, spaces, tabs, and newline chars.
            s = &p[strcspn(p, "#\n\r")];
            *s-- = '\0';
            while ((s >= p) && ((*s == ' ') || (*s == '\t')))
            {
                *s-- = '\0';
            }

            if (*p == '\0') continue; // Check that there is still something left in the string

            groups = p;
            role = strsep(&groups, ":");
            if (groups == nullptr)
            {
                syslog(LOG_WARNING, "read_group_mapping() - Invalid syntax at line %lu in file %s", lineno, fname_r.c_str());
                continue;
            }

            groups += strspn(groups, WHITESPACE);   // Remove leading newline and spaces
            if (groups[0] == '\0')
            {
                syslog(LOG_WARNING, "read_group_mapping() - Invalid syntax at line %lu in file %s", lineno, fname_r.c_str());
                continue;
            }

            role[strcspn(role, WHITESPACE)] = '\0'; // Remove trailing spaces

            group_mapping[role] = split(groups, ", \t");
        }

        fclose(file);
    }

    return group_mapping;
}
