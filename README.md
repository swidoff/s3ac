# s3ac

A small IPython extension that auto-completes s3 URIS.

To install: `pip install s3ac`

```bash
$ ipython
Python 3.9.13 (main, Jun  9 2022, 00:00:00) 
Type 'copyright', 'credits' or 'license' for more information
IPython 8.4.0 -- An enhanced Interactive Python. Type '?' for help.

In [1]: %load_ext s3ac

In [2]: from s3ac import s3

In [3]: s3("<hit tab>
```


To use, start an expression with `s3("`, hit tab, see buckets. After selecting a bucket and hitting tab, `s3
("my_bucket/` will complete prefixes up to the next slash and objects under a prefix ending in a slash.

The s3 function will return a URI (`"s3://my-bucket/dir1/dir2/file.txt"`).

Depends only on boto3 and requires an AWS credentials file in ~/.aws.