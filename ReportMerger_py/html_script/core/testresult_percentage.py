class TestResult_percentage(object):

    def __init__(self,Duplicate_file):
        self.Duplicate_file = Duplicate_file

    def get_testresult_table(self):
        Anchor_tag = self.Duplicate_file.find("a", attrs={"name": "TestOverview"})
        if not Anchor_tag:
            print("[SKIP] Test overview not found")
            return None
        heading = Anchor_tag.find_next("div", class_="Heading4",string=lambda t: t and "Test Results" in t)
        if not heading:
            print("[SKIP] Test Results not found")
            return None
        table = heading.find_next("table")
        if not table:
            print("[SKIP] No table found")
            return None
        return table

    def testresult_percentage(self):
        table = self.get_testresult_table()
        if not table:
            return
        parent_map = {}
        current_group = ""
        for row in table.find_all("tr"):
            cells = row.find_all("td")
            # Detect group header row (<b>)
            if len(cells) >= 2 and cells[0].find("b"):
                current_group = cells[1].get_text(strip=True)
                continue
            if len(cells) >= 3:
                number = cells[0].get_text(strip=True)
                result = cells[-1].get_text(strip=True).lower()
                # Only process valid testcases
                if "." not in number:
                    continue
                parts = number.split(".")
                # Loop through ALL parent levels (including '1')
                for i in range(len(parts)-1, 0, -1):
                    parent_num = ".".join(parts[:i])
                    parent = f"{parent_num} ___ {current_group}"
                    if parent not in parent_map:
                        parent_map[parent] = {"total":0, "pass":0, "fail":0, "inconclusive":0}
                    parent_map[parent]["total"] += 1
                    if result == "pass":
                        parent_map[parent]["pass"] += 1
                    elif result == "fail":
                        parent_map[parent]["fail"] += 1
                    elif result == "inconclusive":
                        parent_map[parent]["inconclusive"] += 1

        for row in table.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) >= 3 and cells[0].find("b"):
                parent_num = cells[0].get_text(strip=True)
                group_tag = cells[1].find("b")
                group_name = group_tag.get_text(strip=True) if group_tag else cells[1].get_text(strip=True)
                matching_data = {"total":0, "pass":0, "fail":0, "inconclusive":0}
                for k, v in parent_map.items():
                    if k.startswith(parent_num + " ___"):
                        matching_data["total"] += v["total"]
                        matching_data["pass"] += v["pass"]
                        matching_data["fail"] += v["fail"]
                        matching_data["inconclusive"] += v["inconclusive"]
                # If nothing found → skip
                if matching_data["total"] == 0:
                    print(f"[MISS] {parent_num} ___ {group_name}")
                    continue
                data = matching_data
                result_td = cells[2]
                inner_table = result_td.find("table")
                if not inner_table:
                    continue
                # Clear existing content
                inner_table.clear()
                new_tr = self.Duplicate_file.new_tag("tr")
                total = data["total"]
                passed = data["pass"]
                failed = data["fail"]
                inconc = data["inconclusive"]
                # Avoid division by zero
                if total == 0:
                    continue
                # Pass %
                if passed > 0:
                    pass_td = self.Duplicate_file.new_tag("td")
                    pass_td["class"] = "PositiveResultCell"
                    pass_td["width"] = f"{(passed/total)*100:.2f}%"
                    pass_td.string = str(passed)
                    new_tr.append(pass_td)
                # Fail %
                if failed > 0:
                    fail_td = self.Duplicate_file.new_tag("td")
                    fail_td["class"] = "NegativeResultCell"
                    fail_td["width"] = f"{(failed/total)*100:.2f}%"
                    fail_td.string = str(failed)
                    new_tr.append(fail_td)
                # Inconclusive %
                if inconc > 0:
                    inc_td = self.Duplicate_file.new_tag("td")
                    inc_td["class"] = "NeutralResultCell"
                    inc_td["width"] = f"{(inconc/total)*100:.2f}%"
                    inc_td.string = str(inconc)
                    new_tr.append(inc_td)
                inner_table.append(new_tr)
        for parent , data in parent_map.items():
            print(f"{parent}:{data}")
