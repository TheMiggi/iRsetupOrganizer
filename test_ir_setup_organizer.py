import os
import shutil
import tempfile
import unittest
import zipfile

from ir_setup_organizer import go


class SupplierTargetDirTests(unittest.TestCase):
    def test_go_supplier_target_dir(self):
        target_dir_supplier_go = "GO"
        target_dir_suffix = "/" + target_dir_supplier_go + "/"
        self.assertEqual(target_dir_suffix, "/GO/")

    def test_go_extracts_zip_and_moves_sto_from_nested_folder(self):
        args = type("Args", (), {"debug": False, "sandbox": False, "dryrun": False})()

        with tempfile.TemporaryDirectory() as tmp_dir:
            archive_source_dir = os.path.join(tmp_dir, "archive_source")
            nested_dir = os.path.join(archive_source_dir, "nested", "deep")
            os.makedirs(nested_dir, exist_ok=True)
            sto_path = os.path.join(nested_dir, "GO_26S4_IMSA_720SGT3_LeMans.sto")
            with open(sto_path, "w", encoding="utf-8") as handle:
                handle.write("setup")

            zip_path = os.path.join(tmp_dir, "GO 26S4 IMSA 720SGT3 LeMans.zip")
            with zipfile.ZipFile(zip_path, "w") as archive:
                archive.write(sto_path, arcname=os.path.relpath(sto_path, archive_source_dir))

            shutil.rmtree(archive_source_dir)

            target_dir_prefix = os.path.join(tmp_dir, "target") + os.sep
            target_dir_suffix = "/GO/"

            go(args, tmp_dir, target_dir_prefix, target_dir_suffix)

            expected_file = os.path.join(target_dir_prefix, "mclaren720sgt3", "GO", "2026W04", "GO_26S4_IMSA_720SGT3_LeMans.sto")
            self.assertTrue(os.path.exists(expected_file))


if __name__ == "__main__":
    unittest.main()
