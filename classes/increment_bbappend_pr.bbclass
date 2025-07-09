#
# This class handles the addition of PR values by ADD_PR
#
# When multiple .bbappend files exist for a single package, defining PR values
# in each .bbappend file will cause inconsistencies.
# Therefore, the .bbappend file manages "additive values" and adds them to the
# PR values.
#
# - The ADD_PR variable defines the "additive values" in the .bbappend file
# - After modifying the .bbappend file, increment the "add value
#
# Example definition in .bbappend file:
#   ```
#   ADD_PR += "1"
#   ```
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
}
