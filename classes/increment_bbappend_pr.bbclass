#
# This class handles the addition of PR values by ADD_PR and PROJECT_PR
#
# ADD_PR:
#   When multiple .bbappend files exist for a single package, defining PR values
#   in each .bbappend file will cause inconsistencies.
#   Therefore, the .bbappend file manages "additive values" and adds them to the
#   PR values.
#
#   - The ADD_PR variable defines the "additive values" in the .bbappend file
#   - After modifying the .bbappend file, increment the "add value
#
#   Example definition in .bbappend file:
#     ```
#     ADD_PR += "1"
#     ```
#
# PROJECT_PR_NAME, PROJECT_PR:
#   For project developers using EMLinux, can assign project-specific PR values
#   when making custom modifications within project.
#   If both PROJECT_PR_NAME and PROJECT_PR are set, they are concatenated to the
#   original PR value using +.
#
#   - PROJECT_PR_NAME:
#     Specify project-specific additional PR name within like project.conf on
#     custom layer.
#   - PROJECT_PR:
#     Specify project-specific PR value in recipes within package.bbappend
#
#   Example:
#     Example definition in project.conf:
#       ```
#       PROJECT_PR_NAME = "eml"
#       ```
#
#     Example definition in bash.bbappend file:
#       ```
#       PROJECT_PR = "3"
#       ```
#
#     bitbake variables in these examples:
#       ```
#       BP="bash-5.0"
#       PF="bash-5.0-r0+eml3"
#       PR="r0+eml3"
#       PROJECT_PR="3"
#       PROJECT_PR_NAME="eml"
#       PV="5.0"
#       ```
#

python() {
    add_pr = d.getVar("ADD_PR")
    if add_pr is not None:
        import re
        if re.match("^[0-9. ]+$", add_pr) is None:
            bb.fatal("The ADD_PR variable specified in .bbappend must be a string that can be converted to an int or float type.")

        def to_float(s):
            try:
                return float(s)
            except ValueError:
                return float(0)

        pr = to_float(d.getVar("PR").replace("r", ""))
        for add in add_pr.split(' '):
            pr += to_float(add)
        if pr.is_integer():
            pr = int(pr)
        d.setVar("PR", "r%s" % pr)

    project_pr_name = d.getVar("PROJECT_PR_NAME")
    if project_pr_name is not None:
        pj_pr = d.getVar("PROJECT_PR")
        if pj_pr is not None:
            pr = d.getVar("PR")
            d.setVar("PR", "%s+%s%s" % (pr, project_pr_name, pj_pr))

}
