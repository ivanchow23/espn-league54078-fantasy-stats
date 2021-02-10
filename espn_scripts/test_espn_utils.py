import espn_utils
import unittest

class TestEspnUtils(unittest.TestCase):
    def SetUp(self):
        """ Set-up required items. """
        pass

    def test_parse_metadata_from_player_str(self):
        """ Tests metadata parsing from player string functionality. """
        # Test typical cases
        input_str = "Steven StamkosOTBF"
        expected_output = {'Player': "Steven Stamkos", 'Injury Designation': "O", 'Team': "TB", 'Position': "F"}
        actual_output = espn_utils.parse_metadata_from_player_str(input_str)
        self.assertEquals(expected_output, actual_output)

        input_str = "Steven StamkosTBF"
        expected_output = {'Player': "Steven Stamkos", 'Injury Designation': "", 'Team': "TB", 'Position': "F"}
        actual_output = espn_utils.parse_metadata_from_player_str(input_str)
        self.assertEquals(expected_output, actual_output)

        input_str = "Marc-Andre FleuryVgsG"
        expected_output = {'Player': "Marc-Andre Fleury", 'Injury Designation': "", 'Team': "Vgs", 'Position': "G"}
        actual_output = espn_utils.parse_metadata_from_player_str(input_str)
        self.assertEquals(expected_output, actual_output)

        # Test various position designations
        input_str = "Player OneOAnaF"
        expected_output = {'Player': "Player One", 'Injury Designation': "O", 'Team': "Ana", 'Position': "F"}
        actual_output = espn_utils.parse_metadata_from_player_str(input_str)
        self.assertEquals(expected_output, actual_output)

        input_str = "Player OneOAnaD"
        expected_output = {'Player': "Player One", 'Injury Designation': "O", 'Team': "Ana", 'Position': "D"}
        actual_output = espn_utils.parse_metadata_from_player_str(input_str)
        self.assertEquals(expected_output, actual_output)

        input_str = "Player OneOAnaD, F"
        expected_output = {'Player': "Player One", 'Injury Designation': "O", 'Team': "Ana", 'Position': "D/F"}
        actual_output = espn_utils.parse_metadata_from_player_str(input_str)
        self.assertEquals(expected_output, actual_output)

        input_str = "Player OneOAnaG"
        expected_output = {'Player': "Player One", 'Injury Designation': "O", 'Team': "Ana", 'Position': "G"}
        actual_output = espn_utils.parse_metadata_from_player_str(input_str)
        self.assertEquals(expected_output, actual_output)

        # Test invalid position designations
        input_str = "Player TwoOAnaE"
        expected_output = {'Player': "Player TwoOAnaE", 'Injury Designation': "", 'Team': "", 'Position': ""}
        actual_output = espn_utils.parse_metadata_from_player_str(input_str)
        self.assertEquals(expected_output, actual_output)

        input_str = "Player TwoOAna"
        expected_output = {'Player': "Player Two", 'Injury Designation': "O", 'Team': "Ana", 'Position': ""}
        actual_output = espn_utils.parse_metadata_from_player_str(input_str)
        self.assertEquals(expected_output, actual_output)

        # Test unknown team abbreviation
        input_str = "Player ThreeO123F"
        expected_output = {'Player': "Player ThreeO123", 'Injury Designation': "", 'Team': "", 'Position': "F"}
        actual_output = espn_utils.parse_metadata_from_player_str(input_str)
        self.assertEquals(expected_output, actual_output)

        # Test missing team abbreviation
        input_str = "Another PlayerOF"
        expected_output = {'Player': "Another Player", 'Injury Designation': "O", 'Team': "", 'Position': "F"}
        actual_output = espn_utils.parse_metadata_from_player_str(input_str)
        self.assertEquals(expected_output, actual_output)

        # Test various injury designations
        input_str = "Injured PlayerDBosD"
        expected_output = {'Player': "Injured Player", 'Injury Designation': "D", 'Team': "Bos", 'Position': "D"}
        actual_output = espn_utils.parse_metadata_from_player_str(input_str)
        self.assertEquals(expected_output, actual_output)

        input_str = "Injured PlayerDTDBosD"
        expected_output = {'Player': "Injured Player", 'Injury Designation': "DTD", 'Team': "Bos", 'Position': "D"}
        actual_output = espn_utils.parse_metadata_from_player_str(input_str)
        self.assertEquals(expected_output, actual_output)

        input_str = "Injured PlayerPBosD"
        expected_output = {'Player': "Injured Player", 'Injury Designation': "P", 'Team': "Bos", 'Position': "D"}
        actual_output = espn_utils.parse_metadata_from_player_str(input_str)
        self.assertEquals(expected_output, actual_output)

        input_str = "Injured PlayerIRBosD"
        expected_output = {'Player': "Injured Player", 'Injury Designation': "IR", 'Team': "Bos", 'Position': "D"}
        actual_output = espn_utils.parse_metadata_from_player_str(input_str)
        self.assertEquals(expected_output, actual_output)

        # Test unknown injury designations
        input_str = "Injured Player99BosD"
        expected_output = {'Player': "Injured Player99", 'Injury Designation': "", 'Team': "Bos", 'Position': "D"}
        actual_output = espn_utils.parse_metadata_from_player_str(input_str)
        self.assertEquals(expected_output, actual_output)

        # Test literally an "empty" string
        input_str = "Empty"
        expected_output = {'Player': "", 'Injury Designation': "", 'Team': "", 'Position': ""}
        actual_output = espn_utils.parse_metadata_from_player_str(input_str)
        self.assertEquals(expected_output, actual_output)

        # Test invalid inputs
        input_str = None
        expected_output = {'Player': "", 'Injury Designation': "", 'Team': "", 'Position': ""}
        actual_output = espn_utils.parse_metadata_from_player_str(input_str)
        self.assertEquals(expected_output, actual_output)

        # Test invalid inputs
        input_str = 12345
        expected_output = {'Player': "", 'Injury Designation': "", 'Team': "", 'Position': ""}
        actual_output = espn_utils.parse_metadata_from_player_str(input_str)
        self.assertEquals(expected_output, actual_output)

        input_str = [1, 2, 3]
        expected_output = {'Player': "", 'Injury Designation': "", 'Team': "", 'Position': ""}
        actual_output = espn_utils.parse_metadata_from_player_str(input_str)
        self.assertEquals(expected_output, actual_output)

    def TearDown(self):
        """ Remove any items. """
        pass