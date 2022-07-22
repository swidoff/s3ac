import itertools
from typing import List

import boto3
import pytest
from moto import mock_s3

import s3ac

# noinspection PyProtectedMember
from s3ac import _list_s3_buckets as list_s3_buckets, _list_s3_keys as list_s3_keys, _completion as completion


@pytest.fixture(autouse=True, scope="module")
def s3_mock_client():
    with mock_s3():
        s3ac.client = boto3.client("s3", region_name="us-west-2")
        location = {"LocationConstraint": "us-west-2"}
        for i in range(1, 4):
            s3ac.client.create_bucket(Bucket=f"bucket{i}", CreateBucketConfiguration=location)

        prefixes = list(map("".join, itertools.product("abc", "abc")))
        for prefix1 in prefixes:
            s3ac.client.put_object(Bucket="bucket1", Key=f"{prefix1}/file.bin", Body=b"")
            s3ac.client.put_object(Bucket="bucket1", Key=f"{prefix1}.bin", Body=b"")
            for prefix2 in prefixes:
                s3ac.client.put_object(Bucket="bucket1", Key=f"{prefix1}/{prefix2}.bin", Body=b"")
                s3ac.client.put_object(Bucket="bucket1", Key=f"{prefix1}/{prefix2}/file.bin", Body=b"")

        yield s3ac.client


def test_list_s3_buckets():
    assert list_s3_buckets() == [f"bucket{i}" for i in range(1, 4)]


@pytest.mark.parametrize(
    "key_prefix,expected",
    [
        ("a", ["aa/", "ab/", "ac/", "aa.bin", "ab.bin", "ac.bin"]),
        ("aa", ["aa/", "aa.bin"]),
        (
            "aa/",
            [f"aa/{''.join(prefix)}/" for prefix in itertools.product("abc", "abc")]
            + [f"aa/{''.join(prefix)}.bin" for prefix in itertools.product("abc", "abc")]
            + ["aa/file.bin"],
        ),
        ("aa/ab", ["aa/ab/", "aa/ab.bin"]),
        ("aa/ab/", ["aa/ab/file.bin"]),
    ],
)
def test_list_s3_keys(key_prefix: str, expected: List[str]):
    assert list_s3_keys("bucket1", key_prefix) == expected


@pytest.mark.parametrize(
    "text,expected",
    [
        ("", ["bucket1/", "bucket2/", "bucket3/"]),
        ("bu", ["bucket1/", "bucket2/", "bucket3/"]),
        ("bucket1", ["bucket1/"]),
        (
            "bucket1/",
            [f"bucket1/{''.join(prefix)}/" for prefix in itertools.product("abc", "abc")]
            + [f"bucket1/{''.join(prefix)}.bin" for prefix in itertools.product("abc", "abc")],
        ),
        (
            "bucket1/a",
            ["bucket1/aa.bin", "bucket1/aa/", "bucket1/ab.bin", "bucket1/ab/", "bucket1/ac.bin", "bucket1/ac/"],
        ),
        ("bucket1/aa", ["bucket1/aa.bin", "bucket1/aa/"]),
        (
            "bucket1/aa/",
            [f"bucket1/aa/{''.join(prefix)}.bin" for prefix in itertools.product("abc", "abc")]
            + [f"bucket1/aa" f"/{''.join(prefix)}/" for prefix in itertools.product("abc", "abc")]
            + ["bucket1/aa/file.bin"],
        ),
    ],
)
def test_completion(text: str, expected: List[str]):
    class MockIPCompleter:
        def __init__(self):
            self.text_until_cursor = f"s3('" + text

    # noinspection PyTypeChecker
    assert completion(MockIPCompleter(), text) == sorted(expected)
