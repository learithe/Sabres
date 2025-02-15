"""
Subscript of Sabres to parse Varscan .vcf outputs for resistance detection
"""

import os
import datetime
from io import StringIO
import pandas as pd

pd.set_option('display.max_rows', None)
neworder = [
    'Filename',
    'REF',
    'POS',
    'ALT',
    'REFPOSALT',
    'HET',
    'DP',
    'FREQ'
]

def file_cleanup(file):
    """
    Remove the lines of the vcf file that contain the ##
    """
    with open(file, 'r') as vcf:
        oneline = ''
        lines = vcf.readlines()
        for line in lines:
            if not line.startswith('##'):
                oneline += line
        return oneline

def file2df(file):
    """
    Sets up the read of varscan vcf file without the seriously unnecessary hashes,
    also will print which file is being read for the log.
    """
    now = datetime.datetime.now()
    time_log = now.strftime("%Y-%m-%d %H:%M:%S")
    print(f"{time_log}: Reading File - {file}")
    return pd.read_csv(StringIO(file_cleanup(file)), sep='\t', header = 0)

def varscan_setup(file):
    """
    converting tsv to dataframe and begin removing unwanted columns
    generates new column called REFPOSALT
    """
    vcf_df = pd.DataFrame(file2df(file))
    if vcf_df.empty:
        return vcf_df
    vcf_df = vcf_df[['REF', 'POS', 'ALT', 'INFO', 'Sample1']]
    vcf_df[['adp', 'wt', 'HET', 'hom', 'nc']] = vcf_df.INFO.str.split(
        ';', expand=True
    )
    vcf_df[[
        'GT',
        'GQ',
        'SDP',
        'DP',
        'RD',
        'AD',
        'FREQ',
        'PVAL',
        'RBQ',
        'ABQ',
        'RDF',
        'RDR',
        'ADF',
        'ADR']] = vcf_df.Sample1.str.split(
            ':', expand=True
        )
    vcf_df['REFPOSALT'] = vcf_df['REF'] + vcf_df['POS'].astype(str) + vcf_df['ALT']
    vcf_df['Filename'] = os.path.splitext(
        os.path.basename(file)
    )[0]
    str_rm = '|'.join(['.varscan.snps'])
    vcf_df['Filename'] = vcf_df['Filename'].str.replace(
        str_rm, ''
    )
    vcf_df=vcf_df.reindex(columns=neworder)
    return vcf_df
