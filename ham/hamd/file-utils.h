#ifndef __FILE_UTILS_H__
#define __FILE_UTILS_H__

#include <string>
#include <vector>
#include <map>

#if __GNUC_PREREQ(8,0) // If GCC >= 8.0
#   include <filesystem>
    typedef std::filesystem::path                 path_t;
#else
#   include <experimental/filesystem>
    typedef std::experimental::filesystem::path   path_t;
#endif // __GNUC_PREREQ(8,0)


std::vector<std::string/*filename*/> sorted_filelist(const path_t & dir_path_r = "");
std::map<std::string/*role*/, std::vector<std::string>/*groups*/> read_group_mapping(const path_t & fname_r);


#endif // __FILE_UTILS_H__
