#!/usr/bin/env python3
"""
This file is executed as a means to build the project before pushing.
I tried getting it to work with github actions, but trust me, all that stuff wasn't easy to get to work.
"""

import sys
import subprocess

# build the full README-file:

with open("docs/usage-guides/quick-start.md", "r") as f:
    quick_start_guide = f.read()
with open("docs/usage-guides/README-template.md", "r") as readme_template_file:
    with open("README.md", "w") as readme_file:
        readme_file.write(readme_template_file.read().format(
            quick_start=quick_start_guide
        ))

# push:

for command in [
    "git add *",
    "git commit -m \"" + sys.argv[1] + "\"",
    "git push"
]:
    print("command:", command)
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    output, error = process.communicate()
