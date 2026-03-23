from core.validator import TestValidator
import copy


class HTMLMerger():

    def __init__(self, Duplicate_file,file_soups):
        self.Duplicate_file = Duplicate_file
        self.file_soups = file_soups

    # Insertion of data based on the comparision made in extract block method.
    def Insert_end_of_Unit(self, content_to_insert):

    # Find parent table of that <td>
        end_unit_cell = self.Duplicate_file.find("td", string=lambda s:s and "End of Test Unit:" in s)
        if not end_unit_cell:
            print("No 'End of Test Unit:' found. Appending at end.")
            if self.Duplicate_file.body:
                self.Duplicate_file.body.append(content_to_insert)
            else:
                self.Duplicate_file.append(content_to_insert)
            return self.Duplicate_file
        target_table = end_unit_cell.find_parent("table")
        if target_table:
            for element in content_to_insert:
                target_table.insert_before(element)
        return self.Duplicate_file
    
    def insert_end_of_Group_fixture(self, content_to_insert, group_name):
        #find table for that <td>
        end_unit_cell= self.Duplicate_file.find("td", string=lambda f:f and "End of Test Group:" in f and group_name in f)
        if not end_unit_cell:
            print("No 'End of Test Group:' found. Appending at end.")
            if self.Duplicate_file.body:
                for element in content_to_insert:
                    self.Duplicate_file.body.append(element)
            else:
                self.Duplicate_file.append(content_to_insert)
            return self.Duplicate_file
        target_table = end_unit_cell.find_parent("table")
        if target_table:
            for element in content_to_insert:
                target_table.insert_before(element)
            print("Inserted before 'End of test group:'")
        return self.Duplicate_file
    
    def insert_end_of_testfixture(self, content_to_copy, fixture_name):
        fixture_tag = self.Duplicate_file.find("a",string=lambda f: f and "Test Fixture:" in f and fixture_name in f)
        if not fixture_tag:
            print(f"Fixture not found in base: {fixture_name}")
            return self.Duplicate_file
        fixture_table = fixture_tag.find_parent("table")
        fixture_id = fixture_table.find("a")["id"].replace("lnk_", "")
        result_table = fixture_table.find_next("table", id=lambda x: x and x.startswith("tbl_t"))
        if not result_table:
            print(f"Result table not found: {fixture_name}")
            return self.Duplicate_file
        target_row = result_table.find("tr", id="on")
        if not target_row:
            print("Target row not found")
            return self.Duplicate_file
        target_cell = target_row.find("td")
        for element in content_to_copy:
            target_cell.append(element)
        print(f"Inserted TC into fixture: {fixture_name}")
        return self.Duplicate_file


    # Extract data wrapper - for tc, fixture, group, unit
    def extract_block(self,start_element, start_node, end_node, name):
        current_element = start_element.find_parent("table")
        collect_data = []
        print(f"Processing: {start_element}")
        while current_element:
            collect_data.append(copy.deepcopy(current_element))
            text = current_element.get_text(" ",strip=True)
            clean_text = text.strip()
            if end_node in clean_text and name in clean_text:
                break
            current_element = current_element.find_next_sibling()
            if not current_element:
                break
            if current_element.name == "table":
                text = current_element.get_text(" ", strip=True)
            if start_node in text and name not in text:
                break
        return collect_data
    

    # Check if data is available in files and, if yes merge them accordingly
    def merge_groups(self, soup):
        groups = soup.find_all("a", string=lambda s: s and "Test Group:" in s)
        for group in groups:
            group_text = group.get_text(" ",strip=True)
            group_name = group_text.split("Test Group:")[-1].strip()
            exists = self.Duplicate_file.find("a",string=lambda s:s and "Test Group:" in s and group_name in s)
            if exists:
                print(f"{group_name} already found in base → skipping")
                continue
            data = self.extract_block(group, "Test Group:", "End of Test Group:", group_name)
            self.Insert_end_of_Unit(data)

    def merge_fixtures(self, soup):
        fixtures = soup.find_all("a", string=lambda f:f and "Test Fixture:" in f)
        for fixture in fixtures:
            fixture_text = fixture.get_text(" ",strip=True)
            fixture_name= fixture_text.split("Test Fixture:")[-1].strip()
            group_tag = fixture.find_previous("a", string=lambda s: s and "Test Group:" in s)
            group_name = group_tag.get_text().split("Test Group:")[-1].strip()
            exists = self.Duplicate_file.find("a", string=lambda f:f and "Test Fixture:" in f and fixture_name in f)
            if exists:
                continue
            data = self.extract_block(fixture, "Test Fixture:", "End of Test Fixture:",fixture_name)
            self.insert_end_of_Group_fixture(data, group_name)
    
    def merge_testcases(self, soup):
        testcases = soup.find_all("a",string=lambda t:t and "TC_" in t)
        for testcase in testcases:
            Start_TC_table = testcase.find_parent("table")
            link_tag = Start_TC_table.find("a", id=True)
            if not link_tag:
                continue
            tc_ID = link_tag["id"].replace("lnk_", "")
            exists = self.Duplicate_file.find("a", string=lambda t: t and t.strip().startswith(tc_ID))
            if exists:
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
            self.insert_end_of_testfixture(collect_TC_data, fixture_name)


    # Merge Test config section based on the test checks above.
    def merge_HTML(self):
        for file ,soup in self.file_soups[1:]:

            if not TestValidator.CheckTestUnit(self.Duplicate_file, soup):
                print("Test Unit mismatch → skipping file")
                continue
            self.merge_groups(soup)
            if TestValidator.CheckTestGroup(self.Duplicate_file, soup):
                self.merge_fixtures(soup)
            if TestValidator.CheckTestFixture(self.Duplicate_file, soup):
                self.merge_testcases(soup)

