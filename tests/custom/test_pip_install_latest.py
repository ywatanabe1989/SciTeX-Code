#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-18 04:32:48 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/tests/custom/test_pip_install_latest.py
# ----------------------------------------
import os

__FILE__ = "./tests/custom/test_pip_install_latest.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-05-18 04:30:08 (ywatanabe)"
# # File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/tests/custom/test_pip_install_latest.py
# # ----------------------------------------
# import os
# __FILE__ = (
#     "./tests/custom/test_pip_install_latest.py"
# )
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------

# import argparse
# from scitex import logging
# import subprocess

# import requests


# def get_latest_release_tag(repository):
#     """
#     Fetch the latest release tag from a GitHub repository.

#     Example
#     -------
#     repo = "ywatanabe1989/scitex"
#     tag = get_latest_release_tag(repo)
#     print(tag)

#     Parameters
#     ----------
#     repository : str
#         GitHub repository in the format "username/repository"

#     Returns
#     -------
#     str or None
#         Latest release tag if found, None otherwise
#     """
#     url = f"https://api.github.com/repos/{repository}/tags"
#     response = requests.get(url)
#     tags = response.json()
#     return tags[0]["name"] if tags else None


# def install_package(repository, tag):
#     """
#     Install a package from GitHub using pip and a specific tag.

#     Example
#     -------
#     repo = "ywatanabe1989/scitex"
#     tag = "v1.0.0"
#     install_package(repo, tag)

#     Parameters
#     ----------
#     repository : str
#         GitHub repository in the format "username/repository"
#     tag : str
#         Tag to install

#     Returns
#     -------
#     int
#         Return code of the pip install command
#     """
#     command = f"pip install git+https://github.com/{repository}@{tag}"
#     logging.info(f"Executing: {command}")
#     return subprocess.call(command, shell=True)


# def main():
#     parser = argparse.ArgumentParser(
#         description="Install latest version of a GitHub repository."
#     )
#     parser.add_argument(
#         "repository",
#         help="GitHub repository in the format username/repository",
#     )
#     args = parser.parse_args()

#     logging.basicConfig(
#         level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
#     )

#     latest_tag = get_latest_release_tag(args.repository)
#     if latest_tag:
#         logging.info(f"Installing {args.repository} at tag {latest_tag}")
#         result = install_package(args.repository, latest_tag)
#         if result == 0:
#             logging.info("Installation successful")
#         else:
#             logging.error("Installation failed")
#     else:
#         logging.error("No tags found for the repository.")


# test_main = main

# # def test_main():
# #     """Tests the main functionality with a known repository."""
# #     test_repo = "ywatanabe1989/scitex"

# #     # Test tag fetching
# #     tag = get_latest_release_tag(test_repo)
# #     assert tag is not None, "Failed to fetch latest tag"

# #     # Test package installation
# #     result = install_package(test_repo, tag)
# #     assert result == 0, "Package installation failed"

# if __name__ == "__main__":
#     test_main()

# # EOF

# EOF
