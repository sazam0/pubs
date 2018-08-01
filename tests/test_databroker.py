# -*- coding: utf-8 -*-
import unittest
import os

import dotdot
import fake_env

from pubs import content, databroker, datacache

import str_fixtures
from pubs import endecoder


class TestDataBroker(fake_env.TestFakeFs):

    def test_databroker(self):

        ende = endecoder.EnDecoder()
        page99_metadata = ende.decode_metadata(str_fixtures.metadata_raw0)
        page99_bibentry = ende.decode_bibdata(str_fixtures.bibtex_raw0)

        for db_class in [databroker.DataBroker, datacache.DataCache]:
            self.reset_fs()

            db = db_class('tmp', 'tmp/doc', create=True)

            db.push_metadata('citekey1', page99_metadata)
            self.assertFalse(db.exists('citekey1', meta_check=True))
            self.assertFalse(db.exists('citekey1', meta_check=False))

            db.push_bibentry('citekey1', page99_bibentry)
            self.assertTrue(db.exists('citekey1', meta_check=False))
            self.assertTrue(db.exists('citekey1', meta_check=True))

            self.assertEqual(db.pull_metadata('citekey1'), page99_metadata)
            pulled = db.pull_bibentry('citekey1')['Page99']
            for key in pulled.keys():
                self.assertEqual(pulled[key], page99_bibentry['Page99'][key])
            self.assertEqual(db.pull_bibentry('citekey1'), page99_bibentry)

    def test_existing_data(self):

        ende = endecoder.EnDecoder()
        page99_bibentry = ende.decode_bibdata(str_fixtures.bibtex_raw0)

        for db_class in [databroker.DataBroker, datacache.DataCache]:
            self.reset_fs()

            self.fs.add_real_directory(os.path.join(self.rootpath, 'testrepo'), read_only=False)

            db = db_class('testrepo', 'testrepo/doc', create=False)

            self.assertEqual(db.pull_bibentry('Page99'), page99_bibentry)

            for citekey in ['10.1371_journal.pone.0038236',
                            '10.1371journal.pone.0063400',
                            'journal0063400']:
                db.pull_bibentry(citekey)
                db.pull_metadata(citekey)

            with self.assertRaises(IOError):
                db.pull_bibentry('citekey')
            with self.assertRaises(IOError):
                db.pull_metadata('citekey')

            db.add_doc('Larry99', 'docsdir://Page99.pdf')
            self.assertTrue(content.check_file('testrepo/doc/Page99.pdf', fail=False))
            self.assertTrue(content.check_file('testrepo/doc/Larry99.pdf', fail=False))

            db.remove_doc('docsdir://Page99.pdf')

    def test_push_pull_cache(self):
        db = databroker.DataBroker('tmp', 'tmp/doc', create=True)
        data_in = {'a': 1}
        db.push_cache('meta', data_in)
        data_out = db.pull_cache('meta')
        self.assertEqual(data_in, data_out)

    def test_pull_cache_fails_on_version_mismatch(self):
        db = databroker.DataBroker('tmp', 'tmp/doc', create=True)
        data_in = {'a': 1}
        db.push_cache('meta', data_in)
        ver = databroker.__version__
        databroker.__version__ = '0.0.0'
        try:
            with self.assertRaises(ValueError):
                db.pull_cache('meta')
        finally:
            databroker.__version__ = ver


if __name__ == '__main__':
    unittest.main(verbosity=2)
