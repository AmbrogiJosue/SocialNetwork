from storages.backends.s3boto3 import S3Boto3Storage

class StaticStorage(S3Boto3Storage):
    bucket_name = 'ambrogi-josue-network'
    location = 'static/network'

class MediaStorage(S3Boto3Storage):
    bucket_name = 'ambrogi-josue-network'
    location = 'static/network/images'