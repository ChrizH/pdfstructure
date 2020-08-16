import subprocess
from pathlib import Path
import os


class DocTypeFilter:
    
    def __init__(self, endings=("doc", "docx", "ppt", "pptx", "xls", "xlsx", "odt", "rtf")):
        self.endings = endings if isinstance(endings, (list, tuple)) else (endings)
    
    def test(self, name):
        return name.split(".")[-1].lower() in self.endings


def find_file(root_dir: str, type_filter: DocTypeFilter, print_mod=10) -> iter([Path]):
    processed = 0
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if type_filter.test(file):
                yield Path(root + "/" + file)
                processed += 1
                if print_mod and processed % print_mod == 0:
                    print("\nprocessed {}\n".format(processed))
    print("found {} file-paths".format(processed))


def convert_to_pdf(file_path, output_dir):
    # create lookup file, original doc, converted location
    p = subprocess.run(['/home/christian/Software/jodconverter-cli-4.3.0/bin/jodconverter-cli',
                        # '-i', '/usr/lib/libreoffice',
                        '-f', 'pdf', '-d', output_dir, file_path],
                       stdout=subprocess.PIPE,
                       universal_newlines=True)
    print(p)


def process(root_dir, output_dir):
    doc_filter = DocTypeFilter()
    for file_path in find_file(root_dir, doc_filter):
        print("convert file {}".format(file_path))
        convert_to_pdf(file_path, output_dir)


if __name__ == "__main__":
    # step into dir
    process("/home/christian/Documents/data_recovery_katharina/raw/",
            "/home/christian/Documents/data_recovery_katharina/pdf/")
