#include <pwd.h>                // fgetpwent()

#include "hamd.h"               // hamd_c
#include "subprocess.h"         // run()
#include "file-utils.h"         // sorted_filelist(), read_group_mapping()
#include "../shared/utils.h"    // streq(), LOG_CONDITIONAL()

/**
 * @brief Scan "/etc/passwd" looking for user. If found, return a pointer
 *        to a "struct passwd" containing all the data related to user.
 *
 *        The reason for creating this function instead of using the
 *        stadard POSIX getpwnam(), is that this function doesn't use the
 *        underlying NSS infrastructure. Instead, it access /etc/passwd
 *        directly, which is what we need.
 *
 * @param user The user we're looking for
 *
 * @return If user found, return a pointer to a struct passwd.
 */
static struct passwd * fgetpwnam(const char * user)
{
    struct passwd * pwd = NULL;
    FILE          * f   = fopen("/etc/passwd", "re");
    if (f)
    {
        struct passwd * ent;
        while (NULL != (ent = fgetpwent(f)))
        {
            if (streq(ent->pw_name, user))
            {
                pwd = ent;
                break;
            }
        }
        fclose(f);
    }

    return pwd;
}

/**
 * @brief Create a new user
 *
 * @param login     User's login name
 * @param roles     List of roles
 * @param hashed_pw Hashed password. Must follow useradd's --password
 *                  syntax.
 *
 * @return Empty string on success, Error message otherwise.
 */
std::string  hamd_c::create_user(const std::string                & login,
                                 const std::vector< std::string > & roles,
                                 const std::string                & hashed_pw)
{
    std::string cmd = "/usr/sbin/useradd"
                      " --create-home"
                      " --user-group"
                      " --password '" + hashed_pw + "'";

    if (!config_rm.shell().empty())
        cmd += " --shell " + config_rm.shell();

    std::string groups = get_groups_as_string(roles);
    if (!groups.empty())
        cmd += " --groups " + groups;

    cmd += ' ' + login;

    LOG_CONDITIONAL(is_tron(), LOG_DEBUG, "hamd_c::create_user() - Create user \"%s\" [%s]", login.c_str(), cmd.c_str());

    int          rc;
    std::string  std_err;
    std::string  std_out;
    std::tie(rc, std_out, std_err) = run(cmd);

    LOG_CONDITIONAL(is_tron(), LOG_DEBUG, "hamd_c::create_user() - Create user \"%s\" rc=%d, stdout=%s, stderr=%s",
                    login.c_str(), rc, std_out.c_str(), std_err.c_str());

    if (rc != 0)
    {
        if (std_err.empty())
            return "/usr/sbin/useradd failed with rc=" + std::to_string(rc);

        return "/usr/sbin/useradd failed with " + std_err;
    }

    std::string errmsg = post_create_scripts(login);
    if (!errmsg.empty()) // The errmsg will be empty on success
    {
        // Since we failed to run the port-create
        // scripts, we now need to delete the user.
        delete_user(login);
    }

    return errmsg;
}

/**
 * @brief Delete a user
 *
 * @param login     User's login name
 *
 * @return Empty string on success, Error message otherwise.
 */
std::string hamd_c::delete_user(const std::string & login)
{
    if (::getpwnam(login.c_str()) == nullptr)
    {
        // User doesn't exist...so success!
        return "";
    }

    std::string  pre_delete_msg = pre_delete_scripts(login);

    LOG_CONDITIONAL(is_tron(), LOG_DEBUG, "hamd_c::delete_user() - pre_delete_scripts() %s",
                    pre_delete_msg.empty() ? "success" : pre_delete_msg.c_str());

    std::string  cmd = "/usr/sbin/userdel --force --remove " + login;

    LOG_CONDITIONAL(is_tron(), LOG_DEBUG, "hamd_c::delete_user() - executing command \"%s\"", cmd.c_str());

    int          rc;
    std::string  std_err;
    std::string  std_out;
    std::tie(rc, std_out, std_err) = run(cmd);

    LOG_CONDITIONAL(is_tron(), LOG_DEBUG, "hamd_c::delete_user() - command returned rc=%d, stdout=%s, stderr=%s",
                    rc, std_out.c_str(), std_err.c_str());

    if (rc == 0)
        return "";

    if (std_err.empty())
        return "/usr/sbin/userdel failed with rc=" + std::to_string(rc);

    return "/usr/sbin/userdel failed with " + std_err;
}

/**
 * @brief Create or Modify a user account
 *
 * @param login     User's login name
 * @param roles     List of roles
 * @param hashed_pw Hashed password. Must follow useradd's --password
 *                  syntax.
 */
::DBus::Struct< bool, std::string > hamd_c::useradd(const std::string                & login,
                                                    const std::vector< std::string > & roles,
                                                    const std::string                & hashed_pw)
{
    if (fgetpwnam(login.c_str()) == nullptr)           // User does not exist
    {                                                  // Let's create it.
        ::DBus::Struct< bool, std::string > ret;
        ret._2 = create_user(login, roles, hashed_pw);
        ret._1 = ret._2.empty();
        return ret;
    }

    // User exists so update password and role
    ::DBus::Struct< bool,       /* success */
                    std::string /* errmsg  */ > ret;
    ret = passwd(login, hashed_pw);
    return ret._1/*success*/ ? set_roles(login, roles) : ret;
}

/**
 * @brief Create a new user or modify an existing user
 *
 * @deprecated      This method is deprecated. Use @useradd() instead.
 * @param login     User's login name
 * @param roles     List of roles
 * @param hashed_pw Hashed password. Must follow usermod's --password
 *                  syntax.
 */
::DBus::Struct< bool, std::string > hamd_c::usermod(const std::string                & login,
                                                    const std::vector< std::string > & roles,
                                                    const std::string                & hashed_pw)
{
    return useradd(login, roles, hashed_pw);
}

/**
 * @brief Delete a user account
 */
::DBus::Struct< bool, std::string > hamd_c::userdel(const std::string& login)
{
    ::DBus::Struct< bool,       /* success */
                    std::string /* errmsg  */ > ret;

    ret._2 = delete_user(login);
    ret._1 = ret._2.empty();

    return ret;
}

/**
 * @brief Change user password
 */
::DBus::Struct< bool, std::string > hamd_c::passwd(const std::string& login, const std::string& hashed_pw)
{
    std::string  cmd = "/usr/sbin/usermod --password '" + hashed_pw + "' " + login;

    LOG_CONDITIONAL(is_tron(), LOG_DEBUG, "hamd_c::passwd() - executing command \"%s\"", cmd.c_str());

    int          rc;
    std::string  std_err;
    std::string  std_out;
    std::tie(rc, std_out, std_err) = run(cmd);

    LOG_CONDITIONAL(is_tron(), LOG_DEBUG, "hamd_c::passwd() - command returned rc=%d, stdout=%s, stderr=%s",
                    rc, std_out.c_str(), std_err.c_str());

    ::DBus::Struct< bool,       /* success */
                    std::string /* errmsg  */ > ret;

    ret._1 = rc == 0;
    ret._2 = rc == 0 ? "" : std_err;

    return ret;
}

/**
 * @brief Set user's roles (supplementary groups)
 */
::DBus::Struct< bool, std::string > hamd_c::set_roles(const std::string& login, const std::vector< std::string >& roles)
{
    std::string groups = get_groups_as_string(roles);
    std::string cmd;

    if (!groups.empty())
        cmd = "/usr/sbin/usermod --groups " + groups + ' ' + login;
    else
        cmd = "/usr/sbin/usermod --groups \"\" " + login;

    LOG_CONDITIONAL(is_tron(), LOG_DEBUG, "hamd_c::set_roles() - executing command \"%s\"", cmd.c_str());

    int          rc;
    std::string  std_err;
    std::string  std_out;
    std::tie(rc, std_out, std_err) = run(cmd);

    LOG_CONDITIONAL(is_tron(), LOG_DEBUG, "hamd_c::set_roles() - command returned rc=%d, stdout=%s, stderr=%s",
                    rc, std_out.c_str(), std_err.c_str());

    ::DBus::Struct< bool,       /* success */
                    std::string /* errmsg  */ > ret;

    ret._1 = rc == 0;
    ret._2 = rc == 0 ? "" : std_err;

    return ret;
}

/**
 * @brief Create a group
 */
::DBus::Struct< bool, std::string > hamd_c::groupadd(const std::string& group)
{
    ::DBus::Struct< bool, std::string > ret;
    ret._1 = false;
    ret._2 = "Not implemented";
    return ret;
}

/**
 * @brief Delete a group
 */
::DBus::Struct< bool, std::string > hamd_c::groupdel(const std::string& group)
{
    ::DBus::Struct< bool, std::string > ret;
    ret._1 = false;
    ret._2 = "Not implemented";
    return ret;
}

/**
 * @brief Return the Linux groups associated with the @roles specified.
 *
 * @param roles  List of roles
 *
 * @return A std::set of Linux groups.
 */
std::set<std::string> hamd_c::get_groups(const std::vector< std::string > & roles)
{
    std::set<std::string>  groups; // Use std::set to eliminate duplicates

    std::map<std::string/*role or priv-lvl*/,
             std::vector<std::string>/*groups*/>  group_mapping = read_group_mapping("/etc/sonic/hamd/group-mapping");

    for (auto & role : roles)
    {
        std::copy(group_mapping[role].cbegin(), group_mapping[role].cend(), std::inserter(groups, groups.end()));
#ifndef ROLES_ARE_SAVED_TO_REDIS
        // Currently the roles are saved as Linux groups in /etc/group.
        // In the next iteration the roles will be saved to the REDIS DB
        // and this won;t be needed.
        groups.insert(role);
#endif
    }

    return groups;
}

/**
 * @brief Return the Linux groups associated with the provided @roles.
 *
 * @param roles  List of roles
 *
 * @return A string of comma-separated Linux groups (e.g. "sudo,docker").
 */
std::string hamd_c::get_groups_as_string(const std::vector< std::string > & roles)
{
    std::set<std::string>  groups = get_groups(roles);
    return join(groups.cbegin(), groups.cend(), ",");
}

/**
 * @brief Run the post-create scripts located in
 *        /etc/sonic/hamd/scripts/post-create/.
 *
 * @param login User's login name.
 *
 * @return Empty string on success, error message otherwise.
 */
std::string hamd_c::post_create_scripts(const std::string  & login) const
{
    int          rc;
    std::string  cmd;
    std::string  std_err;
    std::string  std_out;

    for (auto & file : sorted_filelist("/etc/sonic/hamd/scripts/post-create"))
    {
        if (g_file_test(file.c_str(), G_FILE_TEST_IS_EXECUTABLE))
        {
            cmd = file + ' ' + login;
            std::tie(rc, std_out, std_err) = run(cmd);

            if (rc != 0)
                return "Failed to execute " + cmd + ". " + std_err;
        }
        else
        {
            syslog(LOG_WARNING, "\"%s\" is not executable", file.c_str());
        }
    }

    return "";
}

/**
 * @brief Run the post-create scripts located in
 *        /etc/sonic/hamd/scripts/pre-delete/.
 *
 * @param login User's login name.
 *
 * @return Empty string on success, error message otherwise.
 */
std::string hamd_c::pre_delete_scripts(const std::string  & login) const
{
    int                      rc;
    std::string              cmd;
    std::string              std_err;
    std::string              std_out;
    std::vector<std::string> errmsgs;

    for (auto & file : sorted_filelist("/etc/sonic/hamd/scripts/pre-delete"))
    {
        if (g_file_test(file.c_str(), G_FILE_TEST_IS_EXECUTABLE))
        {
            cmd = file + ' ' + login;
            std::tie(rc, std_out, std_err) = run(cmd);

            if (rc != 0)
                errmsgs.push_back("Failed to execute " + cmd + ". " + std_err);
        }
        else
        {
            syslog(LOG_WARNING, "\"%s\" is not executable", file.c_str());
        }

    }

    return join(errmsgs.cbegin(), errmsgs.cend(), ";");
}
