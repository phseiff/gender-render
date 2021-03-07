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
import json
import time
from bs4 import BeautifulSoup
import bs4

from wheezy.template.engine import Engine
from wheezy.template.ext.core import CoreExtension
from wheezy.template.loader import FileLoader


def make_html_from_tex(path_to_tex: str):
    directory, file_name = path_to_tex.rsplit("/", 1)
    print("\n##############\n#\n# " + file_name + "\n#\n##############\n")
    p = subprocess.Popen(["htlatex", file_name, "xhtml, charset=utf-8", " -cunihtf -utf8"], cwd=directory,
                         stdout=subprocess.PIPE, stdin=subprocess.PIPE)

    # convert to html:
    while True:
        try:
            time.sleep(4)
            print("entering \"q\".")
            p.stdin.write(b"q\n")
            p.stdin.flush()
        except BrokenPipeError:
            print("finished creating html file!")
            break

    # get created html:
    with open(path_to_tex.replace(".tex", ".html"), "r") as f:
        html_content = f.read()

    # handle multicolumn:
    html_soup_representation = BeautifulSoup(html_content, "html.parser")
    for e in html_soup_representation.find_all("tr"):
        if (len(e.find_all(recursive=False)) == 2 and len(e.find_all("td", recursive=False)) == 1
                and len(e.find_all("div", {"class": "multicolumn"}, recursive=False)) == 1):
            amount_of_columns_in_table = len(e.parent.find("tr").find_all("td", recursive=False))
            print("multicolumn row - before:", e)
            print("amount_of_columns_in_table:", amount_of_columns_in_table)
            e.td.string = e.div.string
            e.td["colspan"] = amount_of_columns_in_table
            e.div.decompose()
            print("multicolumn row - after:", e, "\n")

    # add linebreak after the header
    html_soup_representation.find("h2", {"class": "titleHead"}).img["alt"] = "gender*render"
    html_soup_representation.find("h2", {"class": "titleHead"}).contents.insert(2,
                                                                                html_soup_representation.new_tag("br"))

    # edit footnotes
    footnote_numbers = set()
    all_footnotes = str()
    for e in html_soup_representation.find_all("span", {"class": "footnote-mark"}):
        if e.sup:
            footnote_number = e.sup.text.lstrip().rstrip()
            if footnote_number not in footnote_numbers:
                footnote_numbers.add(footnote_number)
                parent = e.parent
                e["id"] = footnote_number + "-footnote"
                e.sup.contents = [html_soup_representation.new_tag("a", href="#" + footnote_number + "-footnote-down")]
                e.sup.a.string = footnote_number
                footnote = str()
                in_relevant_area = False
                print("footnote anchor:", e)
                for e2 in parent.find_all(recursive=False):
                    if (e2.name == "span" and not e2.has_attr("id") and e2.find("a", recursive=False)
                            and e2.a.find("sup", recursive=False) and e2.a.sup.text.lstrip().rstrip() == footnote_number):
                        e2.a["href"] = "#" + footnote_number + "-footnote"
                        e2.a.contents.insert(0, bs4.NavigableString("^"))
                        e2.a["id"] = footnote_number + "-footnote-down"
                        footnote += str(e2)
                        print("found relevant area - starter:", e2)
                        e2.decompose()
                        in_relevant_area = True
                    elif in_relevant_area:
                        for e3 in e2.find_all(recursive=True):
                            if e3.has_attr("class") and e3["class"][0].endswith("-8"):
                                break
                        else:
                            if not (e2.has_attr("class") and e2["class"][0].endswith("-8")):
                                in_relevant_area = False
                    if in_relevant_area:
                        footnote += str(e2)
                        e2.decompose()
                print("footnote:", footnote.replace("\n", " "))
                print("footnote_anchor:", e.__str__(), "\n")
                all_footnotes += "<p>" + footnote.replace("\n", " ") + "</p>\n"
    if all_footnotes:
        all_footnotes = "<h3>Footnotes</h3>\n" + all_footnotes
        print("\nall footnotes:\n" + all_footnotes)
        html_soup_representation.html.body.contents.append(BeautifulSoup(all_footnotes, "html.parser"))

    footnote_numbers = sorted(list(footnote_numbers))
    print("footnote_numbers:", footnote_numbers)

    # save modified html
    # with open(path_to_tex.rsplit("/", 1)[0] + "/index.html", "w") as f:
    with open(path_to_tex.replace(".tex", ".html"), "w") as f:
        f.write(str(html_soup_representation.prettify()))


def make_html_for_all_specs():
    with open("docs/specs/specs.txt", "r") as f:
        list_of_specs = f.read().split("\n")
    for spec_name in list_of_specs:
        with open("docs/specs/" + spec_name + "/versions.tex", "r") as f:
            list_of_versions = f.read().split("\n")
        for version in list_of_versions:
            make_html_from_tex("docs/specs/" + spec_name + "/spec-" + version + ".tex")  # ToDo?


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
        full_path_to_versioned_location_of_spec = os.path.join(spec_dir, "spec-" + version + ".tex")  # ToDo?
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
    else:
        main()
