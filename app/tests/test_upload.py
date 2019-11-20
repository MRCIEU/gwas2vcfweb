import requests
import os


def test_upload(url):
    r = requests.post(url + "/txt/upload", data={
        'chr_col': 1,
        'pos_col': 2,
        'snp_col': 3,
        'ea_col': 4,
        'oa_col': 5,
        'eaf_col': 10,
        'beta_col': 6,
        'se_col': 7,
        'pval_col': 9,
        'ncontrol_col': 8,
        'delimiter': 'tab',
        'header': 'True',
        'gzipped': 'False',
        'build': 'GRCh37'
    }, files={'gwas_file': open(os.path.join('tests', 'data', 'example.1k.txt'), 'rb')})

    assert r.status_code == 201
    assert 'job' in r.json()
