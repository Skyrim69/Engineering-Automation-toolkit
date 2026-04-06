class Statistics_update(object):
    
    def __init__(self, Duplicate_file):
        self.Duplicate_file = Duplicate_file

    def get_statistics_table(self):

        Anchor_tag = self.Duplicate_file.find("a", attrs={"name": "TestOverview"})
        if not Anchor_tag:
            print("[SKIP] Test overview not found")
            return None
        heading = Anchor_tag.find_next("div", class_="Heading4",string=lambda t: t and "Statistics" in t)
        if not heading:
            print("[SKIP] Statistics section not found")
            return None
        table = heading.find_next("table")
        if not table:
            print("[SKIP] No table found")
            return None
        return table

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
    
    def extract_statistics(self,table):

        stats={}
        for rows in table.find_all("tr"):
            cells = rows.find_all("td")
            if len(cells)>=2:
                label = cells[0].get_text(strip=True)

                if label == "Executed test cases":
                    stats["executed"] = int(cells[1].get_text(strip=True))
                
                elif label == "Test cases passed":
                    stats["passed"] = int(cells[1].get_text(strip=True))
                    text = cells[2].get_text(strip=True).split()
                    stats["passed_percentage"] = text[0]
                    text.pop(0)
                    stats["passed_suffix"] = " ".join(text)

                elif label == "Test cases inconclusive":
                    stats["inconclusive"] = int(cells[1].get_text(strip=True))
                    text = cells[2].get_text(strip=True).split()
                    stats["inconclusive_percentage"] = text[0]
                    text.pop(0)
                    stats["inconclusive_suffix"] = " ".join(text)

                elif label == "Test cases failed":
                    stats["failed"] = int(cells[1].get_text(strip=True))
                    text = cells[2].get_text(strip=True).split()
                    stats["failed_percentage"] = text[0]
                    text.pop(0)
                    stats["failed_suffix"] = " ".join(text)
        return stats
    
    def extract_result(self,result_table):

        total = 0
        passed = 0
        inconclusive = 0
        failed = 0
        for row in result_table.find_all("tr"):
            cells = row.find_all("td")

            if len(cells)>=3:
                first_cell = cells[0].get_text(strip=True)
            
                if first_cell == "1.1":
                    inner_table = cells[2].find("table")

                    if inner_table:
                        numbers = [
                            int(td.get_text(strip=True))
                            for td in inner_table.find_all("td")
                            if td.get_text(strip=True).isdigit()
                        ]
                        total = sum(numbers)

                        if len(numbers) ==1:
                            passed = numbers[0]

                        elif len(numbers) ==2:
                            passed,failed = numbers

                        elif len(numbers) >=3:
                            passed,inconclusive,failed =numbers[:3]

        passed_percent = (passed / total)*100 if total else 0
        failed_percent = (failed / total)*100 if total else 0
        inconclusive_percent = (inconclusive / total)*100 if total else 0

        return {
            "total" : total,
            "passed" : passed, 
            "passed_percent" : f"{passed_percent:.1f}%",
            "inconclusive" : inconclusive,
            "inconclusive_percent" : f"{inconclusive_percent:.1f}%",
            "failed" : failed, 
            "failed_percent": f"{failed_percent:.1f}%"
        }
    
    def update_statistics(self, table, result,stats):

        for rows in table.find_all("tr"):
            cells = rows.find_all("td")

            if len(cells) >=2:
                label = cells[0].get_text(strip=True)

                if label == "Executed test cases":
                    cells[1].string = str(result["total"])

                elif label == "Test cases passed":
                    cells[1].string = str(result["passed"])
                    new_percent = str(result["passed_percent"])
                    suffix = stats["passed_suffix"]
                    text = new_percent + " " + suffix
                    cells[2].string = text
                
                elif label == "Test cases inconclusive":
                    cells[1].string = str(result["inconclusive"])
                    new_percent = str(result["inconclusive_percent"])
                    suffix = stats["inconclusive_suffix"]
                    text = new_percent + " " + suffix
                    cells[2].string = text
                
                elif label == "Test cases failed":
                    cells[1].string = str(result["failed"])
                    new_percent = str(result["failed_percent"])
                    suffix = stats["failed_suffix"]
                    text = new_percent + " " + suffix
                    cells[2].string = text

    def statistics_2(self):

        table = self.get_statistics_table()
        result_table = self.get_testresult_table()
        if not table or not result_table:
            return
        
        stats_dict = self.extract_statistics(table)
        result_dict = self.extract_result(result_table)
        print(stats_dict)

        if stats_dict.get("executed") != result_dict["total"]:
            print("[WARNING] Mismatch detected!")

        print("Original stats:", stats_dict)
        self.update_statistics(table, result_dict, stats_dict)
        print("Computed results:", result_dict)
