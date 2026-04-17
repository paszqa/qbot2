import unittest

from generatecsv import extract_release_rows


class ExtractReleaseRowsTests(unittest.TestCase):
    def test_extracts_release_rows_from_legacy_markup(self):
        html = """
        <div class="daty-premier-2017">
          <a class="box">
            <div>16 kwi 2026</div>
            <p>Some Game</p>
            <i>Akcja</i>
          </a>
        </div>
        """

        self.assertEqual(extract_release_rows(html), [("16 kwi 2026", "Some Game", "Akcja")])

    def test_extracts_release_rows_when_wrapper_class_changes(self):
        html = """
        <section class="daty-premier-2026">
          <a class="box release">
            <span>Q2 2026</span>
            <h3>Another Game</h3>
            <i>Przygodowa</i>
          </a>
        </section>
        """

        self.assertEqual(extract_release_rows(html), [("Q2 2026", "Another Game", "Przygodowa")])


if __name__ == "__main__":
    unittest.main()
