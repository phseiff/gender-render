import sys
import requests

github_sha = sys.argv[1]
in_file_name = "spec.tex"
in_file_prefix = in_file_name.split(".")[0]
out_file_name = in_file_name.split(".")[0] + ".html"

with open(out_file_name, "w") as f:
    try:
        former_content = requests.get("https://phseiff.com/gender-render/" + out_file_name).text
    except:
        former_content = open("spec.html", "r").read()
    content_of_tex_file = open(in_file_name, "r").read()
    version = content_of_tex_file.split("\\newcommand{\\version}{", 1)[-1].split("}", 1)[0]
    if not ">" + version + "<" in former_content:
        finished_content = former_content.replace(
            "<!--new:" + in_file_prefix + "-->",
            "<!--new:" + in_file_prefix + "-->"
            + '<li><a href="https://github.com/phseiff/gender-render/raw/' + github_sha + "/docs/" + in_file_name + '">'
            + version + "</a></li>"
        )
        f.write(finished_content)
