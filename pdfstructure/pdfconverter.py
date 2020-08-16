import subprocess

from utils import find_file, DocTypeFilter


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
