#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-12-19 15:37:46 (ywatanabe)"
# File: ./Ninja/workspace/formats/json2md.py

THIS_FILE = "/home/ywatanabe/.emacs.d/lisp/Ninja/workspace/formats/json2md.py"

import json
import sys
import argparse


def json2md(obj, level=1):
    output = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            if output:  # Add extra newline between sections
                output.append("")
            output.append("#" * level + " " + str(key))
            if isinstance(value, (dict, list)):
                output.append(json2md(value, level + 1))
            else:
                output.append(str(value) + "\n")
    elif isinstance(obj, list):
        for item in obj:
            if isinstance(item, (dict, list)):
                output.append(json2md(item, level))
            else:
                output.append("* " + str(item))
    return "\n".join(filter(None, output))


def main():
    parser = argparse.ArgumentParser(description="Convert JSON to Markdown")
    parser.add_argument("input", help="Input JSON file")
    parser.add_argument("-o", "--output", help="Output file (default: stdout)")
    args = parser.parse_args()

    try:
        with open(args.input, "r") as f:
            data = json.load(f)

        result = json2md(data)

        if args.output:
            with open(args.output, "w") as f:
                f.write(result)
        else:
            print(result)

    except FileNotFoundError:
        print(f"Error: File {args.input} not found", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

"""
python ./Ninja/workspace/formats/json2md.py
python -m workspace.formats.json2md
"""
# EOF

# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-12-19 15:29:28 (ywatanabe)"
# # File: ./Ninja/workspace/formats/json2md.py

# THIS_FILE = "/home/ywatanabe/.emacs.d/lisp/Ninja/workspace/formats/json2md.py"

# import json
# import sys

# def json2md(obj, level=1):
#     output = []
#     if isinstance(obj, dict):
#         for key, value in obj.items():
#             if output:  # Add extra newline between sections
#                 output.append("")
#             output.append("#" * level + " " + str(key))
#             if isinstance(value, (dict, list)):
#                 output.append(json2md(value, level + 1))
#             else:
#                 output.append(str(value) + "\n")
#     elif isinstance(obj, list):
#         for item in obj:
#             if isinstance(item, (dict, list)):
#                 output.append(json2md(item, level))
#             else:
#                 output.append("* " + str(item))
#     return "\n".join(filter(None, output))

# def main():
#     if len(sys.argv) != 2:
#         print("Usage: json2md.py <input.json>")
#         sys.exit(1)

#     lpath = sys.argv[1].replace("/./", "/")
#     with open(lpath, "r") as f:
#         data = json.load(f)


# if __name__ == "__main__":
#     main()


# """
# python ./Ninja/workspace/formats/json2md.py
# python -m workspace.formats.json2md
# """

# # EOF
