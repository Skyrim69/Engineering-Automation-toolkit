from core.file_parser import Fileparser
from utils.file_loader import fileloader
from core.html_parser import TestConfig_wrapper
from core.testresult_merger import TestResult
from core.testoverview_merger import TestOverview
from core.testoverview_percentage import TestOverview_Percentage
from core.testresult_percentage import TestResult_percentage
from core.statistics_update import Statistics_update

def main ():

    # Load files
    loader = fileloader(r"C:\Siddhant\Trainings\ReportMerger_py\ReportMerger_py\html_reports")
    file_soups = loader.load_files()
    mergedreport = r"C:\Siddhant\Trainings\ReportMerger_py\ReportMerger_py\html_reports\MergedReport\MergedReport.html"

    # Parse respective files
    parser = Fileparser(file_soups)
    basefile = parser.base_file
    duplicatefile = parser.Duplicate_file

    # Apply Test config wrapper
    html_parser = TestConfig_wrapper(file_soups)
    html_parser.test_config_wrapper()

    # Merge Test result
    result = TestResult(duplicatefile, file_soups)
    result.run()

    # Merge Test Overview 
    merger = TestOverview(duplicatefile, file_soups)
    merger.merge_HTML()

    # Update count in test overview
    updater = TestOverview_Percentage(duplicatefile)
    print("\n*************** Test Overview Result update ***************\n")
    if updater.checktestunit():
        if updater.checktestfixture():
            print("Merging at FIXTURE level")
            fixture_count = updater.Extract_fix_Count()
            updater.merge_count(fixture_count, level="fixture")
        if updater.checktestgroup():
            print("Merging at GROUP level")
            group_count = updater.Extract_group_Count()
            updater.merge_count(group_count, level="group")
        print("Merging at UNIT level")
        unit_count = updater.Extract_unit_Count()
        updater.merge_count(unit_count, level="unit")
    
    # Update count in test result
    testresult_update = TestResult_percentage(duplicatefile)
    print("\n*************** Test Result percent update ****************\n")
    testresult_update.testresult_percentage()

    # Update count in statistics section
    statistics = Statistics_update(duplicatefile)
    print("\n*************** Statistics update ****************\n")
    statistics.statistics_2()

    # Save merged output
    with open(mergedreport, "w", encoding="utf-8") as f:
        f.write(str(duplicatefile))

if __name__ == "__main__":
    main()
