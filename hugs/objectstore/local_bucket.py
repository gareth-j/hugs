import tempfile
import datetime
import shutil
import os

from Acquire.ObjectStore import ObjectStore, use_testing_object_store_backend


def bucket_time():
    """ Returns a prettified (maybe) string of the current
        time and date

        Returns:
            str: A formatted version of datetime.now()
    """

    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")


def get_local_bucket(name=None):
    """ Creates and returns a local bucket
        that's created in the user's home directory

        Returns:
            dict: Local bucket
    """

    # Get the path of the user's home directory
    home_path = os.path.expanduser("~")
    hugs_test_buckets = "hugs_tmp/test_buckets"

    if name:
        hugs_test_buckets += "/%s" % name

    local_buckets_dir = os.path.join(home_path, hugs_test_buckets)

    root_bucket = use_testing_object_store_backend(local_buckets_dir)

    bucket = ObjectStore.create_bucket(bucket=root_bucket, bucket_name="hugs_test")

    return bucket



