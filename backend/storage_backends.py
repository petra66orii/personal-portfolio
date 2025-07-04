from storages.backends.s3boto3 import S3Boto3Storage


class MediaStorage(S3Boto3Storage):
    bucket_name = 'personal-portfolio-media-bucket'
    file_overwrite = False
