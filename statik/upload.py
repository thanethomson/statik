# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os

import paramiko

from statik.config import StatikConfig

import logging
logger = logging.getLogger(__name__)

__all__ = [
    'upload_sftp',
]


def mkdir_p(sftp, path):
    """Create remote path including parent directories if needed
    https://stackoverflow.com/a/14819803
    """
    try:
        sftp.chdir(path)
    except IOError:
        dirname, basename = os.path.split(path.rstrip('/'))
        mkdir_p(sftp, dirname)
        sftp.mkdir(basename)
        sftp.chdir(basename)
        return True


def rm_r(sftp, path):
    """Recursively delete contents of path
    https://stackoverflow.com/a/23256181
    """
    files = sftp.listdir(path)
    for f in files:
        filepath = os.path.join(path, f)
        logger.info('Deleting: %s' % (filepath))
        try:
            sftp.remove(filepath)
        except IOError:
            rm_r(sftp, filepath)


def upload_sftp(input_path, output_path, rm_remote=False):
    ssh_config = StatikConfig(input_path).remote['sftp']

    t = paramiko.Transport((ssh_config['server'], 22))

    t.connect(username=ssh_config['username'], password=ssh_config['password'])
    logger.info('Connecting to %s...' % ssh_config['server'])

    sftp = paramiko.SFTPClient.from_transport(t)
    logger.info('Connected to %s...' % ssh_config['server'])

    if rm_remote:
        path = ssh_config['dir-base'] + ssh_config['dir-root']
        rm_r(sftp, path)

    for root, dirs, files in os.walk(output_path):
        for f in files:
            localpath = root + '/' + f
            dirname = root.replace(output_path, ssh_config['dir-root'], 1)
            remotepath = dirname + '/' + f
            logger.info('Publishing: %s' % (ssh_config['dir-base'] + remotepath))
            try:
                mkdir_p(sftp, ssh_config['dir-base'] + dirname)
            except:
                pass
            sftp.put(localpath, ssh_config['dir-base'] + remotepath)

    sftp.close()
    logger.info('Connection closed.')
