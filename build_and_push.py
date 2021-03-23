#!/usr/bin/env python3
"""
This file is executed as a means to build the project before pushing.
I tried getting it to work with github actions, but trust me, all that stuff wasn't easy to get to work.
"""
import ast
import sys
import subprocess
import os
import pathlib
import shutil
import json
import inspect
import pkgutil
import test

try:
    from wheezy.template.engine import Engine
    from wheezy.template.ext.core import CoreExtension
    from wheezy.template.loader import FileLoader
except ImportError:
    pass


wrong_title_section = r"""\title{\begin{center}
           %\BeginAccSupp{method=plain,Alt={\GenderRender\\Specification}}
           \includegraphics{images/title-black.pdf}
           %\EndAccSupp{}
\end{center} Template system and implementation specification for rendering gender-neutral email templates with pronoun information}"""

corrected_title_section = r"""
\newcommand\titlegraphics[1]{%
\begin{center}%
 \includegraphics{#1}%
\end{center}%
}
% end.

\title{
           %\BeginAccSupp{method=plain,Alt={\GenderRender\\Specification}}
           \titlegraphics{images/title-black.pdf}
           %\EndAccSupp{}
Template system and implementation specification for rendering gender-neutral email templates with pronoun information}
"""


def make_html_for_all_specs():
    print("started converting all tex-files to html!\n")
    with open("docs/specs/specs.txt", "r") as f:
        list_of_specs = f.read().split("\n")
    # iterate over all specifications:
    for spec_name in list_of_specs:
        with open("docs/specs/" + spec_name + "/versions.txt", "r") as f:
            list_of_versions = f.read().split("\n")
        # copy images and settings to the specification directory to allow make4ht to convert image files to png:
        images_from = "docs/images"
        images_to = "docs/specs/" + spec_name + "/images"
        shutil.copytree(images_from, images_to)
        # copy styling and configuration files:
        shutil.copyfile("docs/spec-styling.css", "docs/specs/" + spec_name + "/spec-styling.css")
        shutil.copyfile("docs/config.cfg", "docs/specs/" + spec_name + "/config.cfg")
        # iterate over all versions of the spec to convert them to html:
        for version in list_of_versions:
            tex_file_name_base = "docs/specs/" + spec_name + "/" + spec_name + "-" + version
            # do some modifications to the tex file before converting:
            with open(tex_file_name_base + ".tex", "r") as tex_file:
                tex_file_original_content = tex_file.read()
            # assert wrong_title_section in tex_file_original_content
            tex_file_modified_content = tex_file_original_content.replace(wrong_title_section, corrected_title_section)
            with open(tex_file_name_base + ".tex", "w") as tex_file:
                tex_file.write(tex_file_modified_content)
            # convert:
            command = ["make4ht", "-c", "config.cfg", spec_name + "-" + version + ".tex", "fn-in"]
            print("cmd:", *command)
            p = subprocess.Popen(command, cwd="docs/specs/" + spec_name, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
            output, error = p.communicate()
            print("output:", (output.decode("utf-8").rstrip() if output else None))
            print("error:", (error.decode("utf-8").rstrip() if error else None))
            print("\n")
            # replace links to images (and styling) in the generated html with links to the shared image folder in
            # docs/images:
            image_files = [f for f in os.listdir(images_to)]
            html_file_name = tex_file_name_base + ".html"
            with open(html_file_name, "r") as html_file:
                html_content = html_file.read()
            for image_file in image_files:
                if "src='images/" + image_file + "'" in html_content:
                    html_content = html_content.replace("src='images/" + image_file + "'",
                                                        "src='../../images/" + image_file + "'")
            html_content = html_content.replace("href='spec-styling.css'", "href='../../spec-styling.css'")
            with open(html_file_name, "w") as html_file:
                html_file.write(html_content)
            # move original content back to the tex-file:
            with open(tex_file_name_base + ".tex", "w") as tex_file:
                tex_file.write(tex_file_original_content)
            # remove generated files:
            for ending in {"dvi", "idv", "log", "4ct", "4tc", "aux", "lg", "tmp", "xref"}:  # , "css"}:
                os.remove("docs/specs/" + spec_name + "/" + spec_name + "-" + version + "." + ending)
        # move generated images back to the image folder:
        image_files = [f for f in os.listdir(images_to)]
        for image_file in image_files:
            shutil.move(os.path.join(images_to, image_file), os.path.join(images_from, image_file))
        shutil.rmtree(images_to)
        # delete copied styling and configuration file:
        os.remove("docs/specs/" + spec_name + "/spec-styling.css")
        os.remove("docs/specs/" + spec_name + "/config.cfg")


def list_functions(file):
    # inspired from https://stackoverflow.com/a/48809285/9816158
    with open(file, "r") as f:
        p = ast.parse(f.read())

    # get all functions from the given python file.
    return [fun.name for fun in p.body if isinstance(fun, ast.FunctionDef)]


def list_classes(file):
    # taken from https://stackoverflow.com/a/48809285/9816158
    with open(file, "r") as f:
        p = ast.parse(f.read())

    # get all classes from the given python file.
    classes = [c for c in p.body if isinstance(c, ast.ClassDef)]

    out = dict()
    for c in classes:
        out[c.name] = [fun.name for fun in c.body if isinstance(fun, ast.FunctionDef)]

    return out


def all_functions_are_tested_properly() -> int:  # <-- returns # of untested functions/modules/etc
    # get list of modules we need to test:
    gr_submodules_file_names = [("src/" + f) for f in os.listdir("src") if f.endswith(".py")]
    gr_test_modules_file_names = [("test/" + f) for f in os.listdir("test") if f.endswith(".py")]

    # lists to store (potentially fully) tested elements and (fully) untested elements in:
    untested = list()
    tested = list()

    # test files for test presence:
    for modname in gr_submodules_file_names:
        modname_ending = modname.replace("src/", "")
        modname_for_logs = modname_ending.replace(".py", "")
        if modname_ending.startswith("_") and ("test/test" + modname_ending) in gr_test_modules_file_names:
            test_modname = "test/test" + modname_ending
        elif ("test/test_" + modname_ending) in gr_test_modules_file_names:
            test_modname = "test/test_" + modname_ending
        else:
            classes_and_methods_in_module = list_classes(modname)
            if list_functions(modname):
                untested.append("gender_render." + modname_for_logs)
                continue
            for _, methods in classes_and_methods_in_module.items():
                if methods:  # only raise the error if there are actually classes with methods in there.
                    untested.append("gender_render." + modname_for_logs)
            continue
        tested.append("gender_render." + modname_for_logs)
        classes_and_methods_in_module = list_classes(modname)
        functions_in_module = list_functions(modname)
        classes_and_methods_in_test_module = list_classes(test_modname)
        functions_in_test_module = set()
        for _, functions in classes_and_methods_in_test_module.items():
            functions_in_test_module |= set(functions)

        # test classes for test presence:
        for class_name, class_methods in classes_and_methods_in_module.items():
            class_methods = [m for m in class_methods if m == "__init__" or not m.startswith("__")]
            if not class_methods:
                continue  # skipp empty classes like errors and warnings
            if ("Test" + class_name) not in classes_and_methods_in_test_module:
                untested.append("gender_render." + modname_for_logs + "." + class_name)
            else:
                tested.append("gender_render." + modname_for_logs + "." + class_name)
                test_class_methods = classes_and_methods_in_test_module["Test" + class_name]
                # test class methods for test presence:
                for class_method in class_methods:
                    m = ("test_" + class_method) if not class_method.startswith("_") else ("test" + class_method)
                    if m not in test_class_methods:
                        untested.append("gender_render." + modname_for_logs + "." + class_name + "." + class_method)
                    else:
                        tested.append("gender_render." + modname_for_logs + "." + class_name + "." + class_method)
        # test functions for test presence:
        for function in functions_in_module:
            if ("test_" + function) not in functions_in_test_module:
                untested.append("gender_render." + modname_for_logs + "." + function)
            else:
                tested.append("gender_render." + modname_for_logs + "." + function)

    # check which of these are allowed to not be tested:
    with open("test/no-unittest-needed-list.txt", "r") as whitelist:
        whitelisted = set(whitelist.read().split("\n")) - {""}

    whitelisted_and_not_tested = set()
    whitelisted_and_tested = set()
    not_whitelisted_and_not_tested = set()
    for untested_element in untested:
        for whitelisted_element in whitelisted:
            if untested_element.startswith(whitelisted_element):
                whitelisted_and_not_tested.add(untested_element)
                break
        else:
            not_whitelisted_and_not_tested.add(untested_element)
    for tested_element in tested:
        for whitelisted_element in whitelisted:
            if tested_element.startswith(whitelisted_element):
                for tested_element2 in tested:
                    if (tested_element.startswith(tested_element2) and tested_element2.startswith(whitelisted_element)
                            and tested_element != tested_element2):
                        # this means that the bigger context of the element is already in our list
                        break
                else:
                    whitelisted_and_tested.add(tested_element)
                    break

    # print details:
    for header, elements in [
        ("\n# Not tested (bad!):", not_whitelisted_and_not_tested),
        ("\n# Not tested, but no test needed:", whitelisted_and_not_tested),
        ("\n# No test needed, yet still tested (bad!):", whitelisted_and_tested)
    ]:
        print(header)
        if elements:
            for element in sorted(list(elements)):
                print(element)
        else:
            print("None")
    if len(not_whitelisted_and_not_tested) + len(whitelisted_and_tested):
        print("\nUnittest testing is not sufficient.")
    else:
        print("\nTesting passed. All functions have their unittests.")

    return len(not_whitelisted_and_not_tested) + len(whitelisted_and_tested)


def main():
    # helper function to increase a version number

    def increment_version(v: str, level: str) -> str:
        v_list: list = v.split(".")
        assert len(v_list) == 3
        for j in range(len(v_list)):
            v_list[j] = int(v_list[j])
        if level in {"bugfix", "wording"}:
            v_list[2] += 1
        elif level == "minor":
            v_list[1] += 1
            v_list[2] = 0
        elif level == "major":
            v_list[0] += 1
            v_list[1] = 0
            v_list[2] = 0
        for j in range(len(v_list)):
            v_list[j] = str(v_list[j])
        v = ".".join(v_list)
        return v

    # parse commit message, and increment:

    CHANGELOG_FILE = "docs/specs/changelog.json"
    changelog = None
    if not (os.path.exists(CHANGELOG_FILE) and os.path.isfile(CHANGELOG_FILE)):
        with open(CHANGELOG_FILE, "w") as changelog_file:
            changelog_file.write("{}")
        print("Created changelog file!")
    with open(CHANGELOG_FILE, "r+") as changelog_file:
        changelog = json.load(changelog_file)
        changelog_file.seek(0)

        commit_message = sys.argv[1]
        try:
            # we accept messages in the format "text", as well as
            # "[<spec_name>|implementation] ([bugfix|wording|minor|major]): <text>"
            assert "):" in commit_message
            background, text = commit_message.split("): ", 1)
            assert " (" in background
            aspect, level = background.split(" (", 1)
            assert level in {"bugfix", "minor", "major", "wording"}
            if aspect == "implementation":
                file_name = "src/__init__.py"
                left = '\n__version__ = "'
                right = '"\n'
            else:
                file_name = "docs/" + aspect
                left = '\\newcommand{\\version}{v'
                right = '}'
            assert os.path.exists(file_name) and os.path.isfile(file_name)
            with open(file_name, "r+") as f:
                file_content = f.read()
                f.seek(0)
            # with open(file_name, "r+") as f:
                assert left in file_content
                left_wing, rest = file_content.split(left, 1)
                assert right in rest
                old_version, right_wing = rest.split(right, 1)
                new_version = increment_version(old_version, level)
                file_content = left_wing + left + new_version + right + right_wing
                print("file:", file_name)
                print("old version:", old_version)
                print("new version:", new_version)
                if aspect == "implementation" and input("modify implementation version? >> ") != "yes":
                    sys.exit(0)
                f.write(file_content)

                if aspect != "implementation":
                    spec_file_name = aspect.split(".")[0]
                    if spec_file_name not in changelog:
                        changelog[spec_file_name] = {}
                    changelog[spec_file_name][new_version] = text
            json.dump(changelog, changelog_file, indent=4, sort_keys=True)

        except AssertionError:
            print("No version was incremented.")

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
        full_path_to_versioned_location_of_spec = os.path.join(
            spec_dir, spec_file.split(".")[0] + "-" + version + ".tex")
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

    # render specification download list:

    searchpath = ['docs']
    engine = Engine(
        loader=FileLoader(searchpath),
        extensions=[CoreExtension()]
    )
    template = engine.get_template('spec_dl_page_blueprint.html')

    # build the full README-file:

    with open("docs/usage-guides/quick-start.md", "r") as f:
        quick_start_guide = f.read()
    with open("docs/usage-guides/README-template.md", "r") as readme_template_file:
        with open("README.md", "w") as readme_file:
            readme_file.write(readme_template_file.read().format(
                quick_start=quick_start_guide,
                spec_downloads=template.render({"changelog": changelog})
            ))

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


if __name__ == "__main__":
    if "make-html" in sys.argv:
        make_html_for_all_specs()
    elif "check-test-coverage" in sys.argv:
        if not all_functions_are_tested_properly():
            # Apparently, not all methods and functions have their own testing equivalent.
            sys.exit(1)
    else:
        main()
        all_functions_are_tested_properly()
