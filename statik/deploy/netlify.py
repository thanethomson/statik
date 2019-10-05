"""
Deployment support for Netlify (https://netlify.com).

This replaces the original Netlify support in Statik to reduce security concerns.
"""

import os
import os.path
import requests
from collections import OrderedDict, namedtuple
import hashlib
from datetime import datetime
from dateutil.parser import parse as dateutil_parse
import time
import json
from urllib.parse import quote as urllib_quote

from ..errors import ProjectConfigurationError, DeploymentError
from .base import DeploymentMethod

import logging
logger = logging.getLogger(__name__)


ENVVAR_NETLIFY_SITE_ID = 'NETLIFY_SITE_ID'
ENVVAR_NETLIFY_AUTH_TOKEN = 'NETLIFY_AUTH_TOKEN'
NETLIFY_API_ROOT = 'https://api.netlify.com/api/v1'


DeploymentFile = namedtuple('DeploymentFile', ['path', 'url', 'sha1sum'])


class Netlify(DeploymentMethod):

    def __init__(self, config, error_context=None):
        if not isinstance(config, dict):
            raise ProjectConfigurationError(
                message="Netlify deployment configuration must be a key/value pair mapping",
                context=error_context,
            )

        if 'site_id' not in config and ENVVAR_NETLIFY_SITE_ID not in os.environ:
            raise ProjectConfigurationError(
                message="Netlify deployment requires \"site_id\" parameter to be specified in project " +
                    "configuration or \"%s\" environment variable to be set" % ENVVAR_NETLIFY_SITE_ID,
                context=error_context,
            )

        if 'auth_token' not in config and ENVVAR_NETLIFY_AUTH_TOKEN not in os.environ:
            raise ProjectConfigurationError(
                message="Netlify deployment requires \"auth_token\" parameter to be specified in project " +
                    "configuration or \"%s\" environment variable to be set" % ENVVAR_NETLIFY_AUTH_TOKEN,
                context=error_context,
            )

        self.site_id = os.environ.get(ENVVAR_NETLIFY_SITE_ID, config.get('site_id', None))
        self.auth_token = os.environ.get(ENVVAR_NETLIFY_AUTH_TOKEN, config.get('auth_token', None))

        # check that we can actually access the Netlify API with these credentials
        if not self.can_get_site():
            raise ProjectConfigurationError(
                message="Cannot reach Netlify or incorrect credentials for accessing Netlify API",
                context=error_context,
            )

        logger.debug("Successfully validated Netlify configuration (site_id=%s)" % self.site_id)

    def execute(self, source_path):
        """Deploys the files in the given source path to Netlify via the Netlify API."""
        hashes_by_filename, filenames_by_hash = compute_file_hashes(source_path)
        # create a deployment
        deployment = self.netlify_create_deployment(hashes_by_filename)
        # build up a list of all of the files we need to transfer by way of their hashes
        logger.info("Netlify requires us to update %d file(s)" % len(deployment['required']))
        for file_hash in deployment['required']:
            dfs = filenames_by_hash.get(file_hash, None)
            if dfs is None:
                logger.warning("Got unrecognized SHA-1 sum from Netlify: %s" % file_hash)
                continue
            for df in dfs:
                self.netlify_upload_file(deployment['id'], df)

        logger.info("Netlify deployment up-to-date")


    def netlify_get(self, path):
        return requests.get(
            NETLIFY_API_ROOT + path,
            headers={'Authorization': 'Bearer %s' % self.auth_token},
        )

    def netlify_post(self, path, data):
        return requests.post(
            NETLIFY_API_ROOT + path,
            json=data,
            headers={'Authorization': 'Bearer %s' % self.auth_token},
        )

    def netlify_create_deployment(self, hashes_by_filename):
        payload = {'files': OrderedDict(), 'async': True}
        for filename, df in hashes_by_filename.items():
            payload['files'][filename] = df.sha1sum
        logger.debug("Attempting to send deployment data:\n%s" % json.dumps(payload, indent=2))
        resp = self.netlify_post(
            '/sites/%s/deploys' % self.site_id,
            payload,
        )
        if resp.status_code >= 400:
            raise DeploymentError("Failed to create Netlify deployment: %s" % resp.text)
        deployment = resp.json()
        logger.debug("Got response:\n%s" % json.dumps(deployment, indent=2))
        if deployment.get('state') == 'preparing':
            deployment = self.netlify_wait_for_deployment(deployment['id'])
        return deployment

    def netlify_wait_for_deployment(self, deploy_id, max_wait=60*5):
        start_time = datetime.now().timestamp()
        while True:
            resp = self.netlify_get('/sites/%s/deploys/%s' % (self.site_id, deploy_id))
            if resp.status_code >= 400:
                raise DeploymentError(
                    "Got error from Netlify API while waiting for deployment: %s" % resp.text,
                )
            deployment = resp.json()
            if deployment.get('state') in ['prepared', 'uploading', 'uploaded', 'ready']:
                logger.debug("Netlify is ready for deployment:\n%s" % json.dumps(deployment,
                    indent=2))
                return deployment

            if datetime.now().timestamp() - start_time > max_wait:
                raise DeploymentError("Timed out while waiting for Netlify to become ready for deployment")
            logger.debug("Netlify not yet ready for deployment - waiting another 10 seconds")
            time.sleep(10)

    def can_get_site(self):
        resp = self.netlify_get('/sites/%s' % self.site_id)
        if resp.status_code >= 400:
            logger.error("Got response from Netlify API: %s" % resp.text)
            return False
        logger.debug("Successfully validated access to site with ID: %s" % self.site_id)
        return True

    def netlify_upload_file(self, deploy_id, df: DeploymentFile):
        """Attempts to upload the file with the given properties to Netlify. Automatically takes
        into account rate limiting."""
        with open(df.path, 'rb') as f:
            file_data = f.read()

        netlify_path ='/deploys/%s/files/%s' % (deploy_id, df.url)
        logger.debug("Attempting to upload file %s to %s" % (df.path, netlify_path))
        resp = requests.put(
            NETLIFY_API_ROOT + netlify_path,
            data=file_data,
            headers={'Authorization': 'Bearer %s' % self.auth_token},
        )
        if resp.status_code >= 400:
            raise DeploymentError(
                "Failed to upload file: %s (got response: %s)" % (
                    df.path,
                    resp.text,
                ),
            )
        check_rate_limit(resp)


def compute_file_hashes(path: str):
    """Recursively computes the SHA-1 hashes of all files in the given path."""
    logger.info("Computing hashes for all files in output path: %s" % path)

    hashes_by_filename, filenames_by_hash = OrderedDict(), OrderedDict()

    for root, _, files in os.walk(path):
        for name in files:
            full_path = os.path.join(root, name)
            relative_path = full_path.replace(path, '')
            file_hash = sha1sum(full_path)
            df = DeploymentFile(path=full_path, url=path_to_url(relative_path), sha1sum=file_hash)
            hashes_by_filename[relative_path] = df
            if file_hash not in filenames_by_hash:
                filenames_by_hash[file_hash] = [df]
            else:
                filenames_by_hash[file_hash].append(df)

    return hashes_by_filename, filenames_by_hash


def sha1sum(path: str) -> str:
    """Computes the SHA-1 hash of the file at the given path."""
    sha1 = hashlib.sha1()
    with open(path, 'rb') as f:
        while True:
            data = f.read(1024*1024)
            if not data:
                break
            sha1.update(data)

    return sha1.hexdigest()


def check_rate_limit(resp):
    """Checks the given HTTP response's headers for rate limit information (to see if we're being
    throttled now) and, if we're being throttled, wait until the x-ratelimit-reset time."""

    rate_limit_remaining = int(resp.headers.get('x-ratelimit-remaining', -1))
    logger.debug("Netlify rate limit remaining: %d" % rate_limit_remaining)
    if rate_limit_remaining < 1:
        rate_limit_reset = resp.headers.get('x-ratelimit-reset')
        # wait 60 seconds by default
        rate_limit_wait = 60.0
        if rate_limit_reset is not None:
            try:
                rate_limit_wait = dateutil_parse(rate_limit_reset).timestamp() - datetime.now().timestamp()
            except Exception as e:
                logger.error(
                    "Failed to parse rate limit reset header: %s (got error: %s)" % (rate_limit_reset, e),
                )

        if rate_limit_wait > 0:
            logger.info("Waiting %.2f seconds until continuing Netlify API requests to avoid being throttled" % rate_limit_wait)
            time.sleep(rate_limit_wait)


def path_to_url(path: str) -> str:
    """Converts the given OS path to a URL path (should work in an OS-independent manner)."""
    url = ""
    dirname, basename = os.path.split(path)
    while len(basename) > 0:
        url = urllib_quote(basename) + ("/" if len(url) > 0 else "") + url
        dirname, basename = os.path.split(dirname)
    return url

