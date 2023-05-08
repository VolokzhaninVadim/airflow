# Work with tupes
from typing import List
# Work with regular expression
import re
# Work with OS
import os
# Work with S3
from data_source.scraper.s3 import S3


class Backup:
    def __init__(
        self,
        endpoint_url: str,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        bucket: str,
        paths: dict = {
            'dns_path': '/backup/vvy_dns/'
        },
        **kwargs
    ):
        '''
        Backup local files to s3.

        Parameters
        ----------
        endpoint_url : str
            Endpoint url in S3
        aws_access_key_id : str
            Access key in S3
        aws_secret_access_key : str
            Secret access key in S3
        bucket : str,
            Bucket in S3,
        paths : _type_, optional
            Paths to backup, by default {
            'dns_path': '/backup/vvy_dns/'
            }
        '''
        self.endpoint_url = endpoint_url
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.bucket = bucket
        self.s3_args_dict = {
            'endpoint_url': self.endpoint_url,
            'aws_access_key_id': self.aws_access_key_id,
            'aws_secret_access_key': self.aws_secret_access_key,
            'bucket': self.bucket
        }
        self.s3 = S3(**self.s3_args_dict)
        self.paths = paths

    def get_files_name(self, name_list: List[str], replace: str) -> List:
        '''
        Get file names.

        Parameters
        ----------
        name_list : List[str]
            Get files names
        replace : str
            String for replace to ''

        Returns
        -------
        list
            List of result.
        '''
        result_list = [re.sub(replace, '', i) for i in name_list]
        return result_list

    def get_s3_changes(self) -> dict:
        '''
        Get changes for S3.

        Returns
        -------
        dict
            Dict with changes.
        '''

        result = {}
        for path in self.paths.values():
            # Gel local files
            local_result_list = os.listdir(path)
            # Get files from S3
            s3_result_list = self.s3.get_objects_list(start_position=path)
            # Get result
            result = {path: {
                'delete': list(set(s3_result_list).difference(set(local_result_list))),
                'add': list(set(local_result_list).difference(set(s3_result_list)))
            }}
        return result

    def update_s3(self) -> None:
        '''
        Update files in s3.
        '''
        result = self.get_s3_changes()
        for key in result.keys():
            result_path = result.get(key)
            if result_path['delete']:
                [self.s3.delete_file(file_name=f'{key}{i}'[1:]) for i in result_path['delete']]
            if result_path['add']:
                [self.s3.save_file(path_to_file=f'{key}{i}', path_s3=key[1:len(key) - 1]) for i in result_path['add']]
