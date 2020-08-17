# /home/christian/work/private/data-recovery/namefinder/renamed
import csv
from pathlib import Path
from shutil import copyfile

import pandas as pd

from pdfstructure.utils import find_file, DocTypeFilter
from pdfstructure.title_finder import DocumentTitleExtractor


def rename_copy_file(source, dest_name, destination):
    copyfile(source, destination + "/" + dest_name)


def process_renaming(original_docs_path, destination_path, mapping):
    for path in find_file(original_docs_path, DocTypeFilter(), print_mod=False):
        if not path.is_file():
            continue
        
        fname, doc_type = path.name.split(".")
        
        parent = path.parent.name if not path.parent.name.isnumeric() else path.parent.parent.name
        
        if fname not in mapping or fname in ("5866", "13142"):
            print("unnamed {}".format(path.absolute()))
            renamed_name = fname
            destination_parent = Path(destination_path + "/bilder/")
        else:
            renamed_name = ".".join((mapping[fname], fname))
            destination_parent = Path(destination_path + "/" + parent)
        
        if not destination_parent.exists():
            destination_parent.mkdir()
        
        rename_copy_file(str(path.absolute()), renamed_name[:200] + "." + doc_type, str(destination_parent.absolute()))


def process_title_extraction(root_dir):
    with open(root_dir + '/names.tsv', 'w', newline='') as file:
        writer = csv.writer(file, quoting=csv.QUOTE_NONNUMERIC,
                            delimiter='\t', quotechar='"')
        
        for path in find_file(root_dir, DocTypeFilter(endings="pdf")):
            if not path.is_file():
                continue
            try:
                file_path = str(path.absolute())
                tf = DocumentTitleExtractor()
                title = tf.process(file_path)
                writer.writerow([path.name.split(".")[0], title])
                file.flush()
            except TypeError as e:
                print("ignore {}".format(path))


def load_mapping(path):
    mapping = pd.read_csv(path, delimiter="\t", quotechar='"', names=["fid", "title"])
    
    mapping["fid"] = mapping["fid"].astype("str")
    mapping["title"] = mapping["title"].astype("str")
    
    mask = (mapping["title"].str.len() <= 5)
    df = mapping.loc[mask]
    print("errornous docs")
    print(df)
    
    return mapping.set_index("fid")


if __name__ == "__main__":
    mapping_path = "/home/christian/Documents/data_recovery_katharina/pdf/names.tsv"
    raw = "/home/christian/Documents/data_recovery_katharina/raw/"
    pdf_base = "/home/christian/Documents/data_recovery_katharina/pdf/"
    destination = "/home/christian/Documents/data_recovery_katharina/renamed/"
    # destination = "/home/christian/work/private/data-recovery/namefinder/renamed/"
    
    # process_title_extraction(pdf_base)
    mapping = load_mapping(mapping_path)
    process_renaming(raw, destination, mapping.to_dict()["title"])
