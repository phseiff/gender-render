#!/usr/bin/env python3
"""
This file is executed as a means to build the project before pushing.
I tried getting it to work with github actions, but trust me, all that stuff wasn't easy to get to work.
"""

import sys
import subprocess
import os
import pathlib
import shutil

# build the full README-file:

with open("docs/usage-guides/quick-start.md", "r") as f:
    quick_start_guide = f.read()
with open("docs/usage-guides/README-template.md", "r") as readme_template_file:
    with open("README.md", "w") as readme_file:
        readme_file.write(readme_template_file.read().format(
            quick_start=quick_start_guide
        ))

# index specification versions:

specification_files = [f for f in os.listdir("docs") if os.path.isfile(os.path.join("docs", f)) and f.endswith(".tex")]
for spec_file in specification_files:
    # determine the path for the specification:
    spec_dir = os.path.join("docs", "specs", spec_file.rsplit(".", 1)[0])
    pathlib.Path(spec_dir).mkdir(parents=True, exist_ok=True)

    # determine the version of the given specification:
    full_path_to_spec = os.path.join("docs", spec_file)
    with open(full_path_to_spec, "r") as f:
        version = f.read().split("version}{")[1].split("}")[0]
    print(spec_file, "is at version", version)
    print("full path to spec is", full_path_to_spec)

    # check if version already exists:
    full_path_to_versioned_location_of_spec = os.path.join(spec_dir, "spec-" + version + ".tex")
    if os.path.exists(full_path_to_versioned_location_of_spec):
        print("already exists!\n")
        continue
    print("does not already exist!")

    # otherwise, create a pdf version of it:
    for i in range(3):
        process = subprocess.Popen("pdflatex " + spec_file, shell=True, stdout=subprocess.PIPE, cwd="docs")
        output, error = process.communicate()
        if error:
            print("error:", error)
            sys.exit(1)

    # move newly created pdf version and tex file to specs folder:
    full_path_to_spec_pdf = full_path_to_spec.rsplit(".", 1)[0] + ".pdf"
    full_path_to_versioned_location_of_spec_pdf = full_path_to_versioned_location_of_spec.rsplit(".", 1)[0] + ".pdf"
    shutil.copyfile(full_path_to_spec, full_path_to_versioned_location_of_spec)  # <- tex
    shutil.copyfile(full_path_to_spec_pdf, full_path_to_versioned_location_of_spec_pdf)  # <- pdf
    shutil.copyfile(full_path_to_spec_pdf, os.path.join(spec_dir, "latest.pdf"))  # <- pdf

    # create listing of all files:
    versions_of_this_specification = [f.split("-")[1].rsplit(".", 1)[0]
                                      for f in os.listdir(spec_dir) if f.endswith(".pdf") and "-" in f]
    with open(os.path.join(spec_dir, "versions.txt"), "w") as spec_versions_file:
        spec_versions_file.write("\n".join(versions_of_this_specification))
    print("")

# save a list of all specifications:
with open("docs/specs/specs.txt", "w") as spec_list_file:
    spec_list_file.write("\n".join([f.rsplit(".", 1)[0] for f in specification_files]))

# push:

for command in [
    "git add .github/*",
    "git add *",
    "git add --force docs/specs/*.pdf",
    "git commit -m \"" + sys.argv[1] + "\"",
    "git push"
]:
    print("command:", command)
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    output, error = process.communicate()
