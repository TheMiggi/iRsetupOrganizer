import unittest


class SupplierTargetDirTests(unittest.TestCase):
    def test_go_supplier_target_dir(self):
        target_dir_supplier_go = "GO"
        target_dir_suffix = "/" + target_dir_supplier_go + "/"
        self.assertEqual(target_dir_suffix, "/GO/")


if __name__ == "__main__":
    unittest.main()
