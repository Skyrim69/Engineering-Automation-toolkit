class TestValidator():
# ----------------------------------
# Check for html report parameters- test unit - test group - test fixture
# ----------------------------------
    @staticmethod
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

    @staticmethod
    def CheckTestGroup(basefile, soup): 

        base_group = basefile.find(string=lambda G: G and "Test Group:" in G)
        other_group = soup.find(string=lambda G: G and "Test Group:" in G)

        if not base_group or not other_group:
            return False

        return base_group.strip() == other_group.strip()

    @staticmethod
    def CheckTestFixture(basefile, soup):

        base_fixture = basefile.find(string=lambda f: f and "Test Fixture:" in f)
        other_Fixture = soup.find(string=lambda f: f and "Test Fixture:" in f)

        if not base_fixture or not other_Fixture:
            return False
        
        return base_fixture.strip() == other_Fixture.strip()