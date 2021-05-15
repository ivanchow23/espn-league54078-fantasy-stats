import os
import statsapi_utils
import unittest

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

class TestStatsApiUtils(unittest.TestCase):
    def SetUp(self):
        """ Set-up required items. """
        pass

    def test_url_to_json(self):
        """ Test functionality to download/save stats API data to JSON given a URL. """
        # Test typical case
        url = "https://statsapi.web.nhl.com/api/v1/teams"
        out_path = os.path.join(SCRIPT_DIR, "out.json")
        statsapi_utils.url_to_json(url, out_path)
        self.assertTrue(os.path.exists(out_path))
        self._rm_file(out_path)

        # Test invalid URL
        url = "https://statsapi.web.nhl.com/ap/v1/teams"
        out_path = os.path.join(SCRIPT_DIR, "out.json")
        statsapi_utils.url_to_json(url, out_path)
        self.assertFalse(os.path.exists(out_path))

        # Test invalid URL
        url = "https://statsapi.web.nhl.com/api/v1/teams/invalid"
        out_path = os.path.join(SCRIPT_DIR, "out.json")
        statsapi_utils.url_to_json(url, out_path)
        self.assertFalse(os.path.exists(out_path))

        # Test invalid URL
        url = "htts://statsapi.web.nhl.com/api/v1/teams"
        out_path = os.path.join(SCRIPT_DIR, "out.json")
        statsapi_utils.url_to_json(url, out_path)
        self.assertFalse(os.path.exists(out_path))

        # Test invalid URL
        url = "https://www.google.com"
        out_path = os.path.join(SCRIPT_DIR, "out.json")
        statsapi_utils.url_to_json(url, out_path)
        self.assertFalse(os.path.exists(out_path))

        # Test invalid URL
        url = 12345
        out_path = os.path.join(SCRIPT_DIR, "out.json")
        statsapi_utils.url_to_json(url, out_path)
        self.assertFalse(os.path.exists(out_path))

        # Test invalid URL
        url = ""
        out_path = os.path.join(SCRIPT_DIR, "out.json")
        statsapi_utils.url_to_json(url, out_path)
        self.assertFalse(os.path.exists(out_path))

        # Test invalid URL
        url = None
        out_path = os.path.join(SCRIPT_DIR, "out.json")
        statsapi_utils.url_to_json(url, out_path)
        self.assertFalse(os.path.exists(out_path))

        # Test invalid output file
        url = "https://statsapi.web.nhl.com/api/v1/teams"
        out_path = os.path.join(SCRIPT_DIR, "out.jsn")
        statsapi_utils.url_to_json(url, out_path)
        self.assertFalse(os.path.exists(out_path))

        # Test invalid output file
        url = "https://statsapi.web.nhl.com/api/v1/teams"
        out_path = os.path.join(SCRIPT_DIR, "out.csv")
        statsapi_utils.url_to_json(url, out_path)
        self.assertFalse(os.path.exists(out_path))

        # Test invalid output file
        url = "https://statsapi.web.nhl.com/api/v1/teams"
        out_path = os.path.join(SCRIPT_DIR, "out.jsonn")
        statsapi_utils.url_to_json(url, out_path)
        self.assertFalse(os.path.exists(out_path))

        # Test invalid output file
        url = "https://statsapi.web.nhl.com/api/v1/teams"
        out_path = None
        statsapi_utils.url_to_json(url, out_path)
        self.assertFalse(os.path.exists(os.path.join(SCRIPT_DIR, "out.json")))

    def _rm_file(self, file):
        """ Helper function to remove a file. Does nothing if it doesn't exist. """
        try:
            os.remove(file)
        except:
            pass

    def TearDown(self):
        """ Remove any items. """
        pass