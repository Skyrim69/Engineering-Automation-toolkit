from core.validator import TestValidator
import copy


class HTMLMerger():

    def __init__(self, Duplicate_file,file_soups):
        self.Duplicate_file = Duplicate_file
        self.file_soups = file_soups

    def insert_end_of_testunit(self, content_to_insert):
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

    def merge_HTML(self):
        for file ,soup in self.file_soups[1:]:
            if not TestValidator.CheckTestUnit(self.Duplicate_file, soup):
                print("Test Unit mismatch → skipping file")
                continue
            Groups = soup.find_all("a", string=lambda s: s and "Test Group:" in s)

            for group in Groups:
                group_text = group.get_text(" ",strip=True)
                group_name = group_text.split("Test Group:")[-1].strip()
                base_group = self.Duplicate_file.find("a",string=lambda s:s and s.strip()==f"Test Group:{group_name}")
                # group missing test groups
                if base_group:
                    print("Group already found in base → skipping")
                    continue
                if TestValidator.CheckTestUnit(self.Duplicate_file,soup) :
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
                        self.insert_end_of_testunit(collect_data)