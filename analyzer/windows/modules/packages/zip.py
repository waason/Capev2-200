# Copyright (C) 2010-2015 Cuckoo Foundation.
# This file is part of Cuckoo Sandbox - http://www.cuckoosandbox.org
# See the file 'docs/LICENSE' for copying permission.

import logging
import os

from lib.common.abstracts import Package
from lib.common.exceptions import CuckooPackageError
from lib.common.parse_pe import is_pe_image
from lib.common.zip_utils import upload_extracted_files, attempt_multiple_passwords, extract_archive, extract_zip, get_file_names, get_infos, get_interesting_files

log = logging.getLogger(__name__)


class Zip(Package):
    """Zip analysis package."""

    PATHS = [
        ("SystemRoot", "system32", "cmd.exe"),
        ("SystemRoot", "system32", "wscript.exe"),
        ("SystemRoot", "system32", "rundll32.exe"),
        ("SystemRoot", "sysnative", "WindowsPowerShell", "v1.0", "powershell.exe"),
        ("ProgramFiles", "7-Zip", "7z.exe"),
        ("SystemRoot", "system32", "xpsrchvw.exe"),
        ("ProgramFiles", "Microsoft Office", "WINWORD.EXE"),
        ("ProgramFiles", "Microsoft Office", "Office*", "WINWORD.EXE"),
        ("ProgramFiles", "Microsoft Office*", "root", "Office*", "WINWORD.EXE"),
        ("ProgramFiles", "Microsoft Office", "WORDVIEW.EXE"),
        ("ProgramFiles", "Microsoft Office", "EXCEL.EXE"),
        ("ProgramFiles", "Microsoft Office", "Office*", "EXCEL.EXE"),
        ("ProgramFiles", "Microsoft Office*", "root", "Office*", "EXCEL.EXE"),
        ("ProgramFiles", "Microsoft", "Edge", "Application", "msedge.exe"),
    ]

    def start(self, path):
        password = self.options.get("password", "infected")
        try_multiple_passwords = attempt_multiple_passwords(self.options, password)
        appdata = self.options.get("appdata")
        root = os.environ["APPDATA"] if appdata else os.environ["TEMP"]
        file_names = []
        try:
            zipinfos = get_infos(path)
            extract_zip(path, root, password, 0, try_multiple_passwords)
            for f in zipinfos:
                file_names.append(f.filename)
        except CuckooPackageError as e:
            # We should not be trying to do other things if we cannot extract the initial
            # password-protected zip file
            if "Bad password for file" in repr(e):
                raise

            # use 7z on files that Python zip module couldn't handle
            seven_zip_path = self.get_path_app_in_path("7z.exe")
            file_names = get_file_names(seven_zip_path, path)
            if len(file_names):
                extract_archive(seven_zip_path, path, root, password, try_multiple_passwords)

        # If the .zip only contains a 7zip file, then do:
        if len(file_names) == 1 and file_names[0].endswith(".7z"):
            seven_zip_path = self.get_path_app_in_path("7z.exe")
            nested_7z = os.path.join(root, file_names[0])
            file_names = get_file_names(seven_zip_path, nested_7z)
            if len(file_names):
                extract_archive(seven_zip_path, nested_7z, root, password, try_multiple_passwords)

        file_name = self.options.get("file")
        # If no file name is provided via option, discover files to execute.
        if not file_name:
            # If no file names to choose from, bail
            if not len(file_names):
                raise CuckooPackageError("Empty ZIP archive")

            upload_extracted_files(root, file_names)
            ret_list = []

            # Attempt to find at least one valid exe extension in the archive
            interesting_files = get_interesting_files(file_names)

            if not interesting_files:
                log.debug("No interesting files found, auto executing the first file: %s", file_names[0])
                interesting_files.append(file_names[0])

            log.debug("Missing file option, auto executing: %s", interesting_files)
            for interesting_file in interesting_files:
                file_path = os.path.join(root, interesting_file)
                ret_list.append(self.execute_interesting_file(root, interesting_file, file_path))

            return ret_list
        else:
            file_path = os.path.join(root, file_name)
            return self.execute_interesting_file(root, file_name, file_path)
