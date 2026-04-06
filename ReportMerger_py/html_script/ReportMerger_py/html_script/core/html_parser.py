from bs4 import NavigableString
import re

class TestConfig_wrapper(object):

    def __init__(self,file_soups):
        self.file_soups = file_soups
        
    def test_config_wrapper(self):
        for file, soup in self.file_soups:

            Anchor_tag = soup.find("a", attrs={"name": "TestModuleInfo"})
            if Anchor_tag is None:
                print(f"{file}: Anchor not found")
                continue

            Test_config = soup.new_tag("div", id="TestConfig")

            Anchor_tag.insert_after(NavigableString("\n"))
            Anchor_tag.next_sibling.insert_after(Test_config)

            # siblings = Test_config.next_sibling

            # while siblings:
            #     next_sibling = siblings.next_sibling
            #     Test_config.append(siblings)
            #     siblings = next_sibling

            html = str(soup)
            html = re.sub(r"</div>s*</body>", "</div>\n</body>", html)

            with open(file, "w", encoding="utf-8") as f:
                f.write(str(soup))
            print(f"{file} updated successfully")