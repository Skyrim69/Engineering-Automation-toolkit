class TestOverview_Percentage(object):

    def __init__(self, Duplicate_file):
        self.Duplicate_file = Duplicate_file

    def checktestunit(self):
        base_unit = self.Duplicate_file.find(string=lambda U: U and "Test Unit:" in U)
        if not base_unit:
            print("Test Unit not found in file.")
            return False
        return base_unit.strip()

    def checktestgroup(self):
        group_unit = self.Duplicate_file.find(string=lambda g:g and "Test Group:" in g)
        if not group_unit:
            print(f"Test Group not found in file.")
            return
        return group_unit.strip()

    def checktestfixture(self):
        fixture_unit = self.Duplicate_file.find(string=lambda f:f and "Test Fixture:" in f)
        if not fixture_unit:
            print(f"Test Fixture not found in file.")
            return
        return fixture_unit

    def find_result_table(self, anchor):
        current = anchor.find_parent("table")

        while current:
            result = current.find("table", class_="OverviewResultTable")
            if result:
                return result
            current = current.find_previous_sibling("table")

        return None
    

    def Extract_fix_Count(self):
        if self.checktestunit():
            if self.checktestfixture():
                testcases = self.Duplicate_file.find_all("a",string=lambda t:t and "TC_" in t)
                fixture_count = {}
                for testcase in testcases:
                    Start_TC_table = testcase.find_parent("table")
                    result_row = Start_TC_table.find("tr")
                    result_cells = result_row.find_all("td")
                    result = result_cells[1].get("class", [])
                    link_tag = Start_TC_table.find("a", id=True)
                    if not link_tag:
                        continue
                    current = testcase.find_parent("table")
                    fixture_tag = None
                    while current:
                        fixture_tag = current.find_previous("a", string=lambda f: f and "Test Fixture:" in f)
                        if fixture_tag:
                            break
                        current = current.find_previous_sibling("table")
                    if not fixture_tag:
                        print(f"[ERROR] Fixture not found for TC → {testcase}")
                        continue
                    fixture_name = fixture_tag.get_text().split("Test Fixture:")[-1].strip()
                    if fixture_name not in fixture_count:
                        fixture_count[fixture_name] = {
                            "total": 0,
                            "pass": 0,
                            "fail": 0,
                            "inconclusive": 0,
                            "unknown": 0
                        }
                    fixture_count[fixture_name]["total"] +=1

                    if "TestcaseHeadingPositiveResult" in result:
                        fixture_count[fixture_name]["pass"] += 1
                    elif "TestcaseHeadingNegativeResult" in result:
                        fixture_count[fixture_name]["fail"] += 1
                    elif "TestcaseHeadingInconclusiveResult" in result:
                        fixture_count[fixture_name]["inconclusive"] += 1
                    else:
                        fixture_count[fixture_name]["unknown"] += 1
                for fixture, counts in fixture_count.items():
                    print(f"{fixture}: {counts}")
                return fixture_count

    def Extract_unit_Count(self):
        if self.checktestunit():
            testcases = self.Duplicate_file.find_all("a",string=lambda t:t and "TC_" in t)
            Unit_count = {}
            for testcase in testcases:
                Start_TC_table = testcase.find_parent("table")
                result_row = Start_TC_table.find("tr")
                result_cells = result_row.find_all("td")
                result = result_cells[1].get("class", [])
                link_tag = Start_TC_table.find("a", id=True)
                if not link_tag:
                    continue
                unit_tag = testcase.find_previous("a", string=lambda f: f and "Test Unit:" in f)
                if not unit_tag:
                    print("Test Unit not found → skipping TC")
                    continue
                unit_name = unit_tag.get_text().split("Test Unit:")[-1].strip()
                if unit_name not in Unit_count:
                    Unit_count[unit_name] = {
                        "total": 0,
                        "pass": 0,
                        "fail": 0,
                        "inconclusive": 0,
                        "unknown": 0
                    }
                Unit_count[unit_name]["total"] +=1

                if "TestcaseHeadingPositiveResult" in result:
                    Unit_count[unit_name]["pass"] += 1
                elif "TestcaseHeadingNegativeResult" in result:
                    Unit_count[unit_name]["fail"] += 1
                elif "TestcaseHeadingInconclusiveResult" in result:
                    Unit_count[unit_name]["inconclusive"] += 1
                else:
                    Unit_count[unit_name]["unknown"] += 1
            for unit, counts in Unit_count.items():
                print(f"{unit}: {counts}")
            return Unit_count

    def Extract_group_Count(self):
        if self.checktestunit():
            if self.checktestgroup():
                testcases = self.Duplicate_file.find_all("a",string=lambda t:t and "TC_" in t)
                group_count = {}
                for testcase in testcases:
                    Start_TC_table = testcase.find_parent("table")
                    result_row = Start_TC_table.find("tr")
                    result_cells = result_row.find_all("td")
                    result = result_cells[1].get("class", [])
                    link_tag = Start_TC_table.find("a", id=True)
                    if not link_tag:
                        continue
                    group_tag = testcase.find_previous("a", string=lambda f: f and "Test Group:" in f)
                    if not group_tag:
                        print("Group not found → skipping TC")
                        continue
                    group_name = group_tag.get_text().split("Test Group:")[-1].strip()
                    if group_name not in group_count:
                        group_count[group_name] = {
                            "total": 0,
                            "pass": 0,
                            "fail": 0,
                            "inconclusive": 0,
                            "unknown": 0
                        }
                    group_count[group_name]["total"] +=1

                    if "TestcaseHeadingPositiveResult" in result:
                        group_count[group_name]["pass"] += 1
                    elif "TestcaseHeadingNegativeResult" in result:
                        group_count[group_name]["fail"] += 1
                    elif "TestcaseHeadingInconclusiveResult" in result:
                        group_count[group_name]["inconclusive"] += 1
                    else:
                        group_count[group_name]["unknown"] += 1
                for group, counts in group_count.items():
                    print(f"{group}: {counts}")
                return group_count
                
    def merge_count(self, counts_map, level="fixture"):
        """
        level: 'fixture' | 'group' | 'unit'
        """
        if level == "fixture":
            anchors = self.Duplicate_file.find_all("a", string=lambda s: s and "Test Fixture:" in s)
            key_fn = lambda tag: tag.get_text().split("Test Fixture:")[-1].strip()
        elif level == "group":
            anchors = self.Duplicate_file.find_all("a", string=lambda s: s and "Test Group:" in s)
            key_fn = lambda tag: tag.get_text().split("Test Group:")[-1].strip()
        elif level == "unit":
            anchors = self.Duplicate_file.find_all("a", string=lambda s: s and "Test Unit:" in s)
            key_fn = lambda tag: tag.get_text().split("Test Unit:")[-1].strip()
        else:
            print("Invalid level")
            return

        anchor_map = {key_fn(tag): tag for tag in anchors}
        for name, counts in counts_map.items():
            if name not in anchor_map:
                print(f"{level} not found in doc: {name}")
                continue
            anchor = anchor_map[name]
            result_table = self.find_result_table(anchor)
            if not result_table:
                print(f"No result table for {level}: {name}")
                continue
            for cell in result_table.find_all("td"):
                classes = cell.get("class", [])
                if "PositiveResultCell" in classes:
                    cell.string = str(counts["pass"])
                elif "NegativeResultCell" in classes:
                    cell.string = str(counts["fail"])
                elif "InconclusiveResultCell" in classes:
                    cell.string = str(counts["inconclusive"])
            print(f"Updated {level}: {name}")


                    