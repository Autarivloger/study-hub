"""Verify the publication package preserves the app and excludes local files."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('package_pages', ROOT / 'scripts/package-pages.py')
pages = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pages)


class PagesPackageTest(unittest.TestCase):
    def test_real_tracked_site_package(self):
        parent = Path(tempfile.mkdtemp(prefix='studyhub-pages-test-')).resolve()
        self.assertEqual(parent.parent, Path(tempfile.gettempdir()).resolve())
        output = parent / 'site'
        sha = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        result = pages.package_site(ROOT, output, sha)
        expected = set(pages.public_paths(ROOT)) | {'build-info.json'}
        actual = {p.relative_to(output).as_posix() for p in output.rglob('*') if p.is_file()}
        self.assertEqual(actual, expected)
        self.assertFalse((output / '.git').exists())
        self.assertFalse((output / '.github').exists())
        self.assertTrue((output / '.nojekyll').exists())
        for name in pages.REQUIRED:
            self.assertEqual((ROOT / name).read_bytes(), (output / name).read_bytes())
        info = json.loads((output / 'build-info.json').read_text(encoding='utf8'))
        self.assertEqual(info['commit'], sha)
        self.assertEqual(info['htmlSha256'], hashlib.sha256((ROOT / 'study-hub.html').read_bytes()).hexdigest())
        with self.assertRaises(ValueError):
            pages.package_site(ROOT, output, sha)
        print('Verified package:', result['files'], 'tracked files; staging:', output)

    def test_rejects_invalid_revision_and_repository_output(self):
        with self.assertRaises(ValueError):
            pages.package_site(ROOT, ROOT, 'a' * 40)
        with self.assertRaises(ValueError):
            pages.package_site(ROOT, ROOT / 'unused-pages-test-output', 'not-a-commit')


if __name__ == '__main__':
    unittest.main()
