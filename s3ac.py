from functools import lru_cache
from typing import List
import re

import boto3
from IPython.core.completer import IPCompleter
from IPython.core.interactiveshell import InteractiveShell

PREFIX = re.compile(r's3\(["\']')
client = None


def s3(path: str) -> str:
    """Function whose name triggers s3 auto-complete. Returns an s3 URI."""
    return f"s3://{path}"


@lru_cache(maxsize=None)
def _list_s3_buckets() -> List[str]:
    """Returns the list of available buckets in this account."""
    # noinspection PyUnresolvedReferences
    response = client.list_buckets()
    return [bucket_obj["Name"] for bucket_obj in response.get("Buckets", [])]


def _list_s3_keys(bucket: str, key_prefix: str) -> List[str]:
    """Returns the list of folder and file completions for the given prefix"""

    # noinspection PyUnresolvedReferences
    response = client.list_objects_v2(Bucket=bucket, Prefix=key_prefix, Delimiter="/")

    keys = []
    if "CommonPrefixes" in response:
        for obj in response["CommonPrefixes"]:
            keys.append(obj["Prefix"])
    if "Contents" in response:
        for obj in response.get("Contents"):
            keys.append(obj["Key"])
    return keys


def _completion(self: IPCompleter, text: str) -> List[str]:
    line = self.text_until_cursor
    if (match := re.search(PREFIX, line)) is None:
        res = [text]
    else:
        path = line[match.end(0) :]
        if "/" in path:
            bucket, key_prefix = path.split("/", maxsplit=1)
            keys = _list_s3_keys(bucket, key_prefix)
            res = sorted({text + key[len(key_prefix) :] for key in keys})
        else:
            buckets = _list_s3_buckets()
            res = [text + bucket[len(path) :] + "/" for bucket in buckets if bucket.startswith(path)]
    return res


def load_ipython_extension(ipython: InteractiveShell):
    global client
    client = boto3.client("s3")
    ipython.set_custom_completer(_completion, 0)


def unload_ipython_extension(_ipython: InteractiveShell):
    global client
    client = None
    _list_s3_buckets.cache_clear()
