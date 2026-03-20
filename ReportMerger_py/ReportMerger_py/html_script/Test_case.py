from pathlib import Path
from bs4 import BeautifulSoup, NavigableString
import copy, re

script_dir = Path(r"C:\Siddhant\Trainings\ReportMerger_py\ReportMerger_py\html_reports")
MergedReport = r"C:\Siddhant\Trainings\ReportMerger_py\ReportMerger_py\html_reports\MergedReport\MergedReport.html"

files = sorted(f for f in script_dir.glob("*.html") if "MergedReport" not in f.name)

if not files:
    raise FileNotFoundError(f"No *.html file found in {script_dir}")

file_soups = []

for file in files:
    with open(file, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
        file_soups.append((file, soup))

BaseFile = file_soups[0][1]
Duplicate_file = copy.deepcopy(BaseFile)

# ----------------------------------
# Test config wrapper
# ----------------------------------

def TestConfig_wrapper(file_soups):
    for file, soup in file_soups:

        Anchor_tag = soup.find("a", attrs={"name": "TestModuleInfo"})
        if Anchor_tag is None:
            print(f"{file}: Anchor not found")
            continue

        Test_config = soup.new_tag("div", id="TestConfig")

        Anchor_tag.insert_after(NavigableString("\n"))
        Anchor_tag.next_sibling.insert_after(Test_config)

        siblings = Test_config.next_sibling

        while siblings:
            next_sibling = siblings.next_sibling
            Test_config.append(siblings)
            siblings = next_sibling

        html = str(soup)
        html = re.sub(r"</div>s*</body>", "</div>\n</body>", html)

        with open(file, "w", encoding="utf-8") as f:
            f.write(str(soup))

        print(f"{file} has been parsed.")

TestConfig_wrapper(file_soups)

# ----------------------------------
# Check for html report parameters- test unit - test group - test fixture
# ----------------------------------

def CheckTestUnit(basefile, soup):

    base_unit = basefile.find(string=lambda U: U and "Test Unit:" in U)
    other_unit = soup.find(string=lambda U: U and "Test Unit:" in U)

    if not base_unit or not other_unit:
        print("Test Unit not found in one of the files")
        return False
    
    base_clean = base_unit.strip().replace("\n", " ")
    other_clean = other_unit.strip().replace("\n", " ")

    print(f"[DEBUG] Base Unit: {base_clean}")
    print(f"[DEBUG] Other Unit: {other_clean}")
    
    return  base_unit.strip()==other_unit.strip()

def CheckTestGroup(basefile, soup): 

    base_group = basefile.find(string=lambda G: G and "Test Group:" in G)
    other_group = soup.find(string=lambda G: G and "Test Group:" in G)

    if not base_group or not other_group:
        return False

    return base_group.strip() == other_group.strip()

def CheckTestFixture(basefile, soup):

    base_fixture = basefile.find(string=lambda f: f and "Test Fixture:" in f)
    other_Fixture = soup.find(string=lambda f: f and "Test Fixture:" in f)

    if not base_fixture or not other_Fixture:
        return False
    
    return base_fixture.strip() == other_Fixture.strip()

def Insert_end_of_fixture(basefile, content_to_copy, fixture_name):

    fixture_tag = basefile.find("a",string=lambda f: f and "Test Fixture:" in f and fixture_name in f)
    if not fixture_tag:
        print(f"Fixture not found in base: {fixture_name}")
        return basefile
    fixture_table = fixture_tag.find_parent("table")
    fixture_id = fixture_table.find("a")["id"].replace("lnk_", "")
    result_table = basefile.find("table", id=f"tbl_t{fixture_id}")
    if not result_table:
        print(f"Result table not found: {fixture_name}")
        return basefile
    target_row = result_table.find("tr", id="on")
    if not target_row:
        print("Target row not found")
        return basefile
    target_cell = target_row.find("td")
    for element in content_to_copy:
        target_cell.append(element)
    print(f"Inserted TC into fixture: {fixture_name}")
    return basefile


for file, soup in file_soups[1:]:
    if not CheckTestUnit(Duplicate_file, soup):
        print("Test Unit mismatch → skipping file")
        continue
    if CheckTestGroup(Duplicate_file,soup):
        print("Same Test Group Found. Proceed for fixture")
        if CheckTestFixture(Duplicate_file,soup):
            print("Same Test Fixture found. Proceed for TC.")
            testcases = soup.find_all("a",string=lambda t:t and "TC_" in t)
            
            for testcase in testcases:
                Start_TC_table = testcase.find_parent("table")
                link_tag = Start_TC_table.find("a", id=True)
                if not link_tag:
                    continue
                tc_ID = link_tag["id"].replace("lnk_", "")
                testcase_group = Duplicate_file.find("a", string=lambda t: t and t.strip().startswith(tc_ID))
                if testcase_group:
                    print(f"{tc_ID} already present in file.")
                    continue
                fixture_tag = testcase.find_previous("a", string=lambda f: f and "Test Fixture:" in f)
                if not fixture_tag:
                    print("Fixture not found → skipping TC")
                    continue
                fixture_name = fixture_tag.get_text().split("Test Fixture:")[-1].strip()
                tc_div = soup.find("div", id=f"div_{tc_ID}")
                collect_TC_data = []
                collect_TC_data.append(copy.deepcopy(Start_TC_table))
                print(f"{testcase} inserting in Test Fixture")
                if tc_div:
                        collect_TC_data.append(copy.deepcopy(tc_div))
                else:
                    print(f"Body not found :{tc_ID}")
                Insert_end_of_fixture(Duplicate_file, collect_TC_data, fixture_name)

with open(MergedReport, "w", encoding="utf-8") as f:
    f.write(str(Duplicate_file))
                        