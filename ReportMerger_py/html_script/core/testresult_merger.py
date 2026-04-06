import copy

class TestResult(object):

    def __init__(self, Duplicate_file,file_soups):
        self.Duplicate_file = Duplicate_file
        self.file_soups = file_soups

    def get_testresult_table(self,soup):
        Anchor_tag = soup.find("a", attrs={"name" : "TestOverview"})
        if not Anchor_tag:
            print(f"[SKIP] Test overview not found in {soup}")
            return
        heading = Anchor_tag.find_next("div", class_="Heading4", string=lambda t : t and "Test Results" in t )
        if not heading:
            print(f"[SKIP] Test Result not found in {soup}")
        table = heading.find_next("table")
        if not table:
            print(f"[SKIP] No table found after Test Results in {soup}")
        return table

    def find_table_rows(self ,soup):
        for row in soup.find_all("tr"):
            cells = row.find_all("td")
            if not cells:
                continue
            return cells

    def Testresult_wrapper(self, file_soups):
        file_tc_map= {}
        for file, soup in file_soups:
            tc_data ={}
            tc_set = set()
            table = self.get_testresult_table(soup)
            for row in table.find_all("tr"):
                a_tag = row.find("a")
                if not a_tag:
                    continue
                tc_name = a_tag.get_text(strip=True)
                if "TC_" in tc_name:
                    tc_set.add(tc_name)
                    tc_parent = a_tag.find_parent("tr")
                    cells = tc_parent.find_all("td")
                    number = cells[0].get_text(strip=True)
                    cell = cells[2]
                    cls = cell.get("class", [])

                    if "PositiveResultCell" in cls:
                        result = "pass"
                    elif "NegativeResultCell" in cls:
                        result = "fail"
                    elif "InconclusiveResultCell" in cls:
                        result = "inconclusive"
                    elif "ErrorResultCell" in cls:
                        result = "error"
                    else:
                        result = cell.get_text(strip=True).lower()
                    num_split = number.split(".")
                    num_split = num_split[:len(num_split)-1]
                    if "." in number:
                        parent = ".".join(num_split)
                    else:
                        parent = None
                    if tc_name not in tc_data:
                        tc_data[tc_name] = {
                            "number" : number,
                            "parent" : parent,
                            "result" : result
                        }
                    # if tc_name in tc_data:
                    #     print(f"[DUPLICATE TC FOUND] {tc_name}")
            file_tc_map[file] = tc_data
            print(f"[Test Overview] {file.name} -> {len(tc_set)} TCs found")
        return file_tc_map

    def Extract_block(self, TC_name ,soup):
        a_tag = soup.find("a", string=lambda s: s and s.strip() == TC_name)
        if not a_tag:
            return
        start_table = a_tag.find_parent("tr")
        return copy.deepcopy(start_table)
            
    def merge_cases(self, file_tc_map,file_soups):
        basefile = file_soups[0][0]
        basedata = file_tc_map[basefile]

        for (file,soup) in file_soups[1:]:
            otherdata = file_tc_map[file]
            last_child_map = {}
            def sort_key(tc):
                return list(map(int,otherdata[tc]["number"].split(".")))
            
            for TC_name in sorted(otherdata, key=sort_key):
                inserted = False
                if TC_name not in basedata:
                    parent = otherdata[TC_name]["parent"]

                    # --- get parent name from source ---
                    parent_name = None
                    for r in soup.find_all("tr"):
                        tds = r.find_all("td")
                        if tds and tds[0].get_text(strip=True) == parent:
                            parent_name = tds[1].get_text(strip=True)
                            break

                    # --- STEP 1: FIND parent in base ---
                    parent_row = None
                    for row_b in self.Duplicate_file.find_all("tr"):
                        tds = row_b.find_all("td")
                        if not tds:
                            continue

                        if len(tds) < 2:
                            continue
                        num = tds[0].get_text(strip=True)
                        name = tds[1].get_text(strip=True)

                        if num == parent and parent_name in name:
                            parent_row = row_b
                            break

                    # --- STEP 2: IF parent missing → create it ---
                    if not parent_row and parent:
                        parent_source_row = None
                        for r in soup.find_all("tr"):
                            tds = r.find_all("td")
                            if tds and tds[0].get_text(strip=True) == parent:
                                parent_source_row = r
                                break
                        if parent_source_row:
                            parent_copy = copy.deepcopy(parent_source_row)
                            parent_of_parent = ".".join(parent.split(".")[:-1]) if "." in parent else None
                            insert_pos = None
                            if parent_of_parent:
                                for r in self.Duplicate_file.find_all("tr"):
                                    tds = r.find_all("td")
                                    if not tds:
                                        continue
                                    num = tds[0].get_text(strip=True)
                                    if num.startswith(parent_of_parent + "."):
                                        insert_pos = r
                            if not insert_pos:
                                insert_pos = self.Duplicate_file.find_all("tr")[-1]
                            insert_pos.insert_after(parent_copy)
                            parent_row = parent_copy
                            inserted = True
                    
                    # --- fallback for non-numbered parent (like SM) ---
                    if not parent_row and parent_name:
                        for r in self.Duplicate_file.find_all("tr"):
                            tds = r.find_all("td")
                            if len(tds) > 1:
                                name = tds[1].get_text(strip=True)
                                if parent_name and parent_name.strip() == name.strip():
                                    parent_row = r
                                    break

                    # --- STEP 3: INSERT TC (OUTSIDE parent creation block) ---
                    row = self.Extract_block(TC_name, soup)
                    row = copy.deepcopy(row)

                    # --- reuse last inserted child if exists ---
                    last_child = last_child_map.get(parent)
                    if parent not in last_child_map:
                        last_child = None
                        if parent_row:
                            next_row = parent_row.find_next_sibling("tr")
                            while next_row:
                                tds = next_row.find_all("td")
                                if not tds:
                                    break
                                num = tds[0].get_text(strip=True)
                                if parent and not num.startswith(parent + "."):
                                    break
                                last_child = next_row
                                next_row = next_row.find_next_sibling("tr")
                        last_child_map[parent] = last_child
                    last_child = last_child_map[parent]

                    # insert logic
                    if last_child:
                        last_child.insert_after(row)
                        inserted = True
                        last_child_map[parent] = row
                        last_child = row
                    elif parent_row:
                       parent_row.insert_after(row)
                       inserted = True
                    else:
                        # fallback → insert at end
                        self.Duplicate_file.find_all("tr")[-1].insert_after(row)
                        inserted = True
                    basedata[TC_name] = otherdata[TC_name]
                else:
                    baseresult = basedata[TC_name]["result"]
                    otherresult = otherdata[TC_name]["result"]
                    parent = basedata[TC_name]["parent"]
                    parent_row = None
                    for r in self.Duplicate_file.find_all("tr"):
                        tds = r.find_all("td")
                        if len(tds) > 0 and tds[0].get_text(strip=True) == parent:
                            parent_row = r
                            break
                    baseresult = baseresult.strip().lower()
                    otherresult = otherresult.strip().lower()

                    if baseresult in ["fail", "inconclusive"] and otherresult == "pass":
                        row = self.Extract_block(TC_name, soup)
                        row = copy.deepcopy(row)
                        last_child = None
                        if parent:
                            tds = self.find_table_rows(self.Duplicate_file)
                            num = tds[0].get_text(strip=True)
                            if num.startswith(parent + "."):
                                last_child = r

                        existing_row = None
                        for r in self.Duplicate_file.find_all("tr"):
                            a = r.find("a")
                            if a and a.get_text(strip=True) == TC_name:
                                existing_row = r
                                break
                        if existing_row:
                            existing_row.replace_with(row)
                            inserted = True
                        basedata[TC_name] = otherdata[TC_name]
                        print(f"[Test Overview] {TC_name} -> {parent}")
                    elif baseresult in ["inconclusive"] and otherresult =="fail":
                        row = self.Extract_block(TC_name, soup)
                        row = copy.deepcopy(row)
                        last_child = None
                        if parent:
                            tds = self.find_table_rows(self.Duplicate_file)
                            num =tds[0].get_text(strip=True)
                            if num.startswith(parent + "."):
                                last_child = r

                        existing_row = None
                        for r in self.Duplicate_file.find_all("tr"):
                            a = r.find("a")
                            if a and a.get_text(strip=True) == TC_name:
                                existing_row = r
                                break
                        if existing_row:
                            existing_row.replace_with(row)
                            inserted = True
                        basedata[TC_name] = otherdata[TC_name]
                        print(f"[Test Overview] {TC_name} -> {parent}")
                if TC_name not in basedata:
                    print(f"[Test Overview] {TC_name} -> {parent_name}")
                if not inserted and TC_name not in basedata:
                    print(f"[MISS] TC not inserted: {TC_name}")

    def remove_testcases(self):

        table = self.get_testresult_table(self.Duplicate_file)
        rows = table.find_all("tr")
        for row in rows:
            cell = row.find_all("td")
            if len(cell) <3:
                continue
            TC_name = cell[1].get_text(strip=True)
            tc_remove = cell[2].get_text(strip=True)    
            if "not executed" in tc_remove.lower():
                row.decompose()
                print(f"{TC_name} removed from file.")

    def run(self):
        print("\n ************ Test Result Merger *********** \n")
        file_tc_map = self.Testresult_wrapper(self.file_soups)
        self.merge_cases(file_tc_map, self.file_soups)
        self.remove_testcases()
        print("Merging done")




