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
import javalang
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
        self.groups = [self.contents[i:i + 2]
                       for i in range(0, len(self.contents), 2)]
        for info, source in self.groups:
            name, ext = os.path.splitext(info)
            extraction_destination = os.path.join(self.destination, name)
            info_loc, src_loc = (os.path.join(self.destination, info),
                                 os.path.join(self.destination, source))
            print(name)
            print(extraction_destination)
            mkpath(extraction_destination)
            self.move(info_loc, extraction_destination)
            self.move(src_loc, extraction_destination)
        success_file_location = os.path.join(self.destination,
                                             "success_flag.txt")
        with open(success_file_location, 'w') as success_file:
            success_file.write("All files successfully extracted.")

    def already_extracted(self):
        """Check to make sure we aren't unnecessarily re-extracting files"""
        return os.path.exists(os.path.join(self.destination,
                                           "success_flag.txt"))

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
        # Consider using this with a search box that lets
        # you narrow down or only display attempt submissions
        # which match the criteria given by the user.
        pass


class Attempt:
    def __init__(self, path):
        self.path = path
        self.folder_name = os.path.split(path)[-1]
        self.archive_extraction_path = ""
        self.programming_language = "java"
        self.extension_type = "java"
        # Name format: Lab #_
        #              studID01_
        #              attempt_
        #              submission-time_
        #              FileName.archive-ext
        self.folder_info = self.folder_name.split('_')
        self.lab_number = self.folder_info[0]
        self.student_name = self.folder_info[1]
        self.attempt_number = self.folder_info[2]
        self.time = self._get_submission_time()
        self.info = self.read_info_file()
        self.requirements = self.read_requirements_file()
        self.source_paths = self.find_source_code(self.extension_type)
        self.main_class = None
        self.package = None
        self.source = self.read_source_code()
        self.execution_commands = self._get_execution_paths()
        self.valid_attempt = None

    def _get_submission_time(self):
        time_string = self.folder_info[3]
        time = time_string
        # TODO: Fully implement this using Python time-formatting libraries.
        return time

    def read_info_file(self):
        with open(self._get_info_file(), 'r', errors="replace") as file:
            return file.read()

    def read_requirements_file(self):
        # TODO: Unimplemented.
        return "BLARGHish"

    def _get_info_file(self):
        for file in os.listdir(self.path):
            name, ext = os.path.splitext(file)
            if ext == ".txt":
                return os.path.join(self.path, file)
        print("No info file found.")

    def get_main_class_name(self, source):
        try:
            if "main" in source:
                tree = javalang.parse.parse(source)
                for a_type in tree.types:
                    if 'public' in a_type.modifiers:
                        for method in a_type.body:
                            if method.name == "main" and len(method.parameters) == 1\
                                    and "public" in method.modifiers and "static" in method.modifiers\
                                    and method.return_type is None:
                                param = method.parameters[0]
                                if param.type.name == "String" and param.type.dimensions in [[None], []]:
                                    self.main_class = a_type.name
                                    if tree.package.name != "javalang.brewtab.com":
                                        self.package = tree.package.name
        except:
            pass

    def read_source_code(self):
        source = dict()
        for source_file in self.source_paths:
            name = os.path.splitext(os.path.split(source_file)[-1])[0]
            with open(source_file, 'r', errors="replace") as file:
                source[name] = file.read()
                self.get_main_class_name(source[name])
        return source

    @staticmethod
    def search_for_file_type(path, extension):
        # Not sure if this is compatible PY<3.5,
        # check and implement alternatives if required.
        search_string = os.path.join(path, "**", "*." + str(extension))
        return glob.glob(search_string, recursive=True)

    def find_source_code(self, file_extension,
                         extension_search=[".zip", ".rar",
                                           ".tar", ".tar.gz"]):
        """
        Searches the attempt directory for an archive type, extracts it,
        and gets the paths of specific files from the resulting directory.
        :param file_extension: The file extension that you want to search for
        :param extension_search: What file type you're looking
                                 for in the directory.
        :return: A list of paths to every file in the
                 extracted directory that has the specified extension.
        """
        for file in os.listdir(self.path):
            name, ext = os.path.splitext(file)
            if ext in extension_search:
                archive_path = os.path.join(self.path, file)
                self.archive_extraction_path = os.path.join(self.path, name)
                if not os.path.exists(self.archive_extraction_path):
                    mkpath(self.archive_extraction_path)
                    patoolib.extract_archive(
                            archive_path, outdir=self.archive_extraction_path)
                return Attempt.search_for_file_type(
                        self.archive_extraction_path, file_extension)
        print("No archive file found.")

    def _get_execution_paths(self):
        output_dir = os.path.join(self.archive_extraction_path, "bin")
        if not os.path.exists(output_dir):
            mkpath(output_dir)
        formatted_source_paths = ["{}".format(source_path)
                                  for source_path in self.source_paths]
        compilation_script = ["javac", "-Xlint",
                              "-cp", "{src}"
                              .format(src=self.archive_extraction_path),
                              "-d", "{bin}"
                              .format(bin=output_dir),
                              *formatted_source_paths]
        class_to_be_executed = self.package + "." + self.main_class if self.package else self.main_class
        execution_command = ["java", "-cp", "{bin}".format(bin=output_dir), class_to_be_executed]
        return {"compile": compilation_script,
                "execute": execution_command}

    def run_compiled_code(self):
        # TODO: Unimplemented
        pass
