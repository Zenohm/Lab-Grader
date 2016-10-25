"""
This is going to handle taking the grade-book zip file and
extracting it into its own directory, iterating through all
the individual submitted files, extracting the relevant
java source files, displaying the information, and will
potentially provide a nice interface that will allow the TA
to go back and forth through files.
"""
from distutils.dir_util import mkpath
import glob
import os
import patoolib
import shutil



class GradeBook:
    def __init__(self, path):
        self.path = os.path.abspath(path)
        assert os.path.exists(self.path)
        self.name = os.path.split(os.path.splitext(self.path)[0])[-1]
        self.location = os.path.split(os.path.splitext(self.path)[0])[0]
        self.destination = os.path.join(self.location, self.name)
        self.contents = None
        self.groups = None
        self.attempts = list()

    def move(self, src, dst):
        try:
            shutil.move(src, dst)
        except shutil.Error:
            pass

    def extract_all_attempts(self):
        mkpath(self.destination)
        patoolib.extract_archive(self.path, outdir=self.destination)
        self.contents = sorted(os.listdir(self.destination))
        self.groups = [self.contents[i:i + 2] for i in range(0, len(self.contents), 2)]
        for info, source in self.groups:
            name, ext = os.path.splitext(info)
            extraction_destination = os.path.join(self.destination, name)
            info_loc, src_loc = os.path.join(self.destination, info), os.path.join(self.destination, source)
            print(name)
            print(extraction_destination)
            mkpath(extraction_destination)
            self.move(info_loc, extraction_destination)
            self.move(src_loc, extraction_destination)
        with open(os.path.join(self.destination, "success_flag.txt"), 'w') as file:
            file.write("All files successfully extracted.")

    def already_extracted(self):
        return os.path.exists(os.path.join(self.destination, "success_flag.txt"))

    def process_attempt(self, path):
        self.attempts.append(Attempt(path))

    def process_all_attempts(self):
        for folder in os.listdir(self.destination):
            path = os.path.join(self.destination, folder)
            if os.path.isdir(path):
                path = os.path.join(self.destination, folder)
                self.process_attempt(path)

    def filter_attempts(self, name_search, date_search):
        # TODO: Unimplemented
        # Consider using this with a search box that lets you narrow down or only display
        # attempt submissions which match the criteria given by the user.
        pass


class Attempt:
    def __init__(self, path):
        self.path = path
        self.folder_name = os.path.split(path)[-1]
        # Name format: Lab #_studID01_attempt_This-is-a-time_WhateverTheyNamedTheFile.zip
        self.folder_info = self.folder_name.split('_')
        self.lab_number = self.folder_info[0]
        self.student_name = self.folder_info[1]
        self.attempt_number = self.folder_info[2]
        self.time = self._get_submission_time()
        self.info = self.read_info_file()
        self.requirements = "BLARGHish"
        self.source_paths = self.find_source_code("java")
        self.source = self.read_source_code()
        self.valid_attempt = None

    def _get_submission_time(self):
        time_string = self.folder_info[3]
        time = time_string
        # TODO: Fully implement this using Python time-formatting libraries.
        return time

    def read_info_file(self):
        with open(self._get_info_file(), 'r', errors="replace") as file:
            return file.read()

    def _get_info_file(self):
        for file in os.listdir(self.path):
            name, ext = os.path.splitext(file)
            if ext == ".txt":
                return os.path.join(self.path, file)
        print("No info file found.")

    def read_source_code(self):
        source = dict()
        for source_file in self.source_paths:
            name = os.path.splitext(os.path.split(source_file)[-1])[0]
            with open(source_file, 'r', errors="replace") as file:
                source[name] = file.read()
        return source

    def find_source_code(self, file_extension, extension_search=[".zip", ".rar", ".tar", ".tar.gz"]):
        """
        Searches the attempt directory for an archive type, extracts it,
        and gets the paths of specific files from the resulting directory.
        :param file_extension: The file extension that you want to search for
        :param extension_search: What file type you're looking for in the directory.
        :return: A list of paths to every file in the extracted directory that has the specified extension.
        """
        for file in os.listdir(self.path):
            name, ext = os.path.splitext(file)
            if ext in extension_search:
                archive_path = os.path.join(self.path, file)
                archive_extraction_path = os.path.join(self.path, name)
                if not os.path.exists(archive_extraction_path):
                    mkpath(archive_extraction_path)
                    patoolib.extract_archive(archive_path, outdir=archive_extraction_path)
                # Not sure if this is compatible PY<3.5, check and implement alternatives if required.
                search_string = os.path.join(archive_extraction_path, "**", "*." + str(file_extension))
                return glob.glob(search_string, recursive=True)
        print("No archive file found.")

    def compile_source_code(self):
        # TODO: Unimplemented
        pass

    def run_compiled_code(self):
        # TODO: Unimplemented
        pass
