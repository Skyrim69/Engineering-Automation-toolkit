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

        print(f"{file} updated successfully")

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

def Insert_end_of_Unit(basefile, content_to_insert):

    # Find parent table of that <td>
    end_unit_cell = basefile.find("td", string=lambda s:s and "End of Test Unit:" in s)
    if not end_unit_cell:
        print("No 'End of Test Unit:' found. Appending at end.")
        if basefile.body:
            basefile.body.append(content_to_insert)
        else:
            basefile.append(content_to_insert)
        return basefile
    target_table = end_unit_cell.find_parent("table")
    if target_table:
        for element in content_to_insert:
            target_table.insert_before(element)
    return basefile

for file ,soup in file_soups[1:]:
    if not CheckTestUnit(Duplicate_file, soup):
        print("Test Unit mismatch → skipping file")
        continue
    Groups = soup.find_all("a", string=lambda s: s and "Test Group:" in s)

    for group in Groups:
        group_text = group.get_text(" ",strip=True)
        group_name = group_text.split("Test Group:")[-1].strip()
        base_group = Duplicate_file.find("a",string=lambda s:s and s.strip()==f"Test Group:{group_name}")
        # group missing test groups
        if base_group:
            print("Group already found in base → skipping")
        if CheckTestUnit(Duplicate_file,soup) :
            if not base_group:
                start_table = group.find_parent("table")
                current = start_table
                collect_data =[]
                print(f"Processing group: {group_name}")
                while current:
                    collect_data.append(copy.deepcopy(current))
                    text = current.get_text(" ",strip=True)
                    clean_text = text.strip()
                    # END condition
                    if "End of Test Group:" in clean_text and group_name in clean_text:
                        print("Same Test Group END found → stopping")
                        break
                    current = current.find_next_sibling()
                    if not current:
                        break
                    if current.name =="table":
                        text = current.get_text(" ",strip=True)
                    if "Test Group:" in text and group_name not in text:
                        print("New Test Group started → stopping extraction")
                        break
                Insert_end_of_Unit(Duplicate_file,collect_data)

with open(MergedReport, "w", encoding="utf-8") as f:
    f.write(str(Duplicate_file))

