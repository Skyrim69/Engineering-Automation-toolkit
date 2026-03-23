from core.file_parser import Fileparser
from utils.file_loader import fileloader
from core.html_parser import Htmlparser
from core.testoverview_merger import HTMLMerger

def main ():

    # Load files
    loader = fileloader(r"C:\Siddhant\Trainings\ReportMerger_py\ReportMerger_py\html_reports")
    file_soups = loader.load_files()
    mergedreport = r"C:\Siddhant\Trainings\ReportMerger_py\ReportMerger_py\html_reports\MergedReport\MergedReport.html"

    # parse respective files
    parser = Fileparser(file_soups)
    basefile = parser.base_file
    duplicatefile = parser.Duplicate_file

    # Apply Test config wrapper
    html_parser = Htmlparser(file_soups)
    html_parser.test_config_wrapper()

    # merge html 
    merger = HTMLMerger(duplicatefile, file_soups)
    merger.merge_HTML()

    # Save merged output
    with open(mergedreport, "w", encoding="utf-8") as f:
        f.write(str(duplicatefile))

if __name__ == "__main__":
    main()
