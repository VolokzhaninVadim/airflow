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
            'dns_path': '/backup/vvy_dns/',
            'private_cloud_path': '/backup/private_cloud/',
            'private_media_server': '/backup/vvy_media_server/',
            'airflow': '/backup/vvy_airflow/',
            'jupyterlab': '/backup/vvy_jupyterlab/'
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
            'dns_path': '/backup/vvy_dns/',
            'private_cloud_path': '/backup/private_cloud/',
            'private_media_server': '/backup/vvy_media_server/',
            'airflow': '/backup/vvy_airflow',
            'jupyterlab': '/backup/vvy_jupyterlab/'
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
            s3_result_list = [i.replace(path[1:], '') for i in self.s3.get_objects_list(start_position=path[1:])]
            # Get result
            s3_result_list.sort(reverse=True)
            delete_list = [i for i in s3_result_list[2:] if i.endswith('zip')]
            add_list = [i for i in list(set(local_result_list).difference(set(s3_result_list))) if i.endswith('zip')]
            result[path] = {
                'delete': delete_list,
                'add': add_list
            }
        return result

    def update_s3(self, dict_path: str) -> None:
        '''
        Update files in s3.

        Parameters
        ----------
        dict_path : str
            Path in self.paths.
        '''
        result = self.get_s3_changes()
        path = self.paths[dict_path]
        result_path = result.get(path)
        if result_path['delete']:
            [self.s3.delete_file(file_name=f'{path}{i}'[1:]) for i in result_path['delete']]
        elif result_path['add']:
            [self.s3.save_file(path_to_file=f'{path}{i}', path_s3=path[1:] + i) for i in result_path['add']]
            [os.remove(f'{path}{i}') for i in result_path['add']]
