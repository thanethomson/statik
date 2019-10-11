"""
Deployment support for SFTP.
"""

import os
import os.path
import getpass

import paramiko
from .base import DeploymentMethod
from ..errors import ProjectConfigurationError, DeploymentError

import logging
logger = logging.getLogger(__name__)


ENVVAR_SFTP_HOST = "SFTP_HOST"
ENVVAR_SFTP_PORT = "SFTP_PORT"
ENVVAR_SFTP_DEST_PATH = "SFTP_DEST_PATH"
ENVVAR_SFTP_USER = "SFTP_USER"
ENVVAR_SFTP_PASSWORD = "SFTP_PASSWORD"
ENVVAR_SFTP_KEY_FILE = "SFTP_KEY_FILE"
ENVVAR_SFTP_KEY_FILE_PASSWORD = "SFTP_KEY_FILE_PASSWORD"
DEFAULT_SFTP_PORT = 22
DEFAULT_SFTP_KEY_FILE = "~/.ssh/id_rsa"


class SFTP(DeploymentMethod):

    def __init__(self, config, error_context=None):
        self.host = os.environ.get(ENVVAR_SFTP_HOST, config.get('host', None))
        if self.host is None:
            raise ProjectConfigurationError(
                message="Missing host parameter for SFTP deployment",
                context=error_context,
            )

        self.port = int(
            os.environ.get(ENVVAR_SFTP_PORT, config.get('port', DEFAULT_SFTP_PORT))
        )
        self.dest_path = os.environ.get(
            ENVVAR_SFTP_DEST_PATH,
            config.get('dest-path', None),
        )
        if self.dest_path is None:
            raise ProjectConfigurationError(
                message="Missing destination path parameter for SFTP deployment",
                context=error_context,
            )
        self.user = os.environ.get(ENVVAR_SFTP_USER, config.get('user', None))
        if self.user is None:
            raise ProjectConfigurationError(
                message="Missing user parameter for SFTP deployment",
                context=error_context,
            )
        # disallow for specifying passwords via configuration file
        self.password = os.environ.get(ENVVAR_SFTP_PASSWORD, None)
        self.key_file = os.environ.get(
            ENVVAR_SFTP_KEY_FILE,
            config.get('key-file', DEFAULT_SFTP_KEY_FILE),
        )
        self.key_file_password = os.environ.get(
            ENVVAR_SFTP_KEY_FILE_PASSWORD,
            None,
        )
        self.private_key = None
        if self.key_file is not None:
            # in case there's a ~ character in the key file path
            self.key_file = os.path.expanduser(self.key_file)
            logger.debug("Attempting to load SSH key from file: %s" %
                    self.key_file)
            self.private_key = try_load_private_key_interactive(
                self.key_file,
                password=self.key_file_password,
                error_context=error_context,
            )
        if self.password is None and self.private_key is None:
            raise ProjectConfigurationError(
                message="No valid authentication mechanism provided for SFTP deployment",
                context=error_context,
            )
        if self.password is not None and self.private_key is not None:
            logger.debug(
                "Both private key and password are present - favouring "
                "password-based authentication (do not specify a password if you "
                "want to rather use private key-based authentication)"
            )
            self.private_key = None

    def execute(self, source_path):
        copy_via_sftp(
            source_path,
            self.dest_path,
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            pkey=self.private_key,
        )


def copy_via_sftp(source_path, dest_path, host=None, port=None, user=None,
        password=None, pkey=None, rm_dest=False):
    with paramiko.transport.Transport((host, port)) as transport:
        logger.info("Connecting to %s:%d" % (host, port))
        try:
            transport.connect(
                hostkey=get_host_key(host),
                username=user,
                password=password,
                pkey=pkey,
                rm_dest=rm_dest,
            )
        except paramiko.SSHException as e:
            raise DeploymentError("Failed to connect to %s:%d: %s" %
                    (host, port, e))

        copy_via_transport(transport, source_path, dest_path)


def copy_via_transport(transport, source_path, dest_path, rm_dest=False):
    with paramiko.sftp_client.SFTPClient.from_transport(transport) as sftp:
        logger.info("Connected to remote host via SFTP")
        if rm_dest:
            logger.info("Removing destination path on remote host: %s" %
                    dest_path)
            rm_path_via_sftp(sftp, dest_path)

        logger.info("Transferring files from %s (local) to %s (remote)..." %
            (source_path, dest_path))
        for root, _, files in os.walk(source_path):
            # compute a UNIX-like root for the destination folder into which
            # we'll be transferring files
            remote_dir = dest_path + "/" + root.replace(source_path,
                    "").replace("\\", "/").strip("/")
            # ensure the remote directory exists
            sftp_mkdir_p(sftp, remote_dir)
            for f in files:
                local_full_path = os.path.join(root, f)
                remote_full_path = remote_dir + "/" + f
                logger.info("Copying %s to %s..." % (local_full_path,
                    remote_full_path))
                sftp.put(local_full_path, remote_full_path)

        logger.info("Transfer complete!")


def sftp_mkdir_p(sftp, remote_directory):
    """Ensures that the given path exists on the target server.
    Adapted from: https://stackoverflow.com/a/14819803"""
    if remote_directory == '/':
        # absolute path so change directory to root
        sftp.chdir('/')
        return
    if remote_directory == '':
        # top-level relative directory must exist
        return
    try:
        sftp.chdir(remote_directory) # sub-directory exists
    except IOError:
        path_parts = remote_directory.rstrip("/").split("/")
        dirname = "/".join(path_parts[:-1])
        basename = path_parts[-1]
        sftp_mkdir_p(sftp, dirname) # make parent directories
        logger.debug("Creating remote folder: %s" % remote_directory)
        sftp.mkdir(basename) # sub-directory missing, so created it
        sftp.chdir(basename)


def rm_path_via_sftp(sftp, path):
    """Removes the given path using the specified SFTP connection."""
    logger.debug("Removing remote folder and all contents: %s" % path)
    files = sftp.listdir(path)
    for f in files:
        filepath = path.rstrip("/\\") + "/" + f.strip("/\\")
        try:
            sftp.remove(filepath)
        except IOError:
            # it's probably a directory
            rm_path_via_sftp(sftp, filepath)


def try_load_private_key_interactive(filename, password=None,
        error_context=None):
    """Wraps the try_load_private_key method such that it can request a password
    from the user via stdin if necessary."""
    try:
        return try_load_private_key(
            filename,
            password=password,
            error_context=error_context,
        )
    except paramiko.PasswordRequiredException:
        print("The SSH key %s requires a password")
        password = getpass.getpass("Please enter the password for this key:")
        return try_load_private_key(
            filename,
            password=password,
            error_context=error_context,
        )


def try_load_private_key(filename, password=None, error_context=None):
    """Attempts to load a private key from the given file. Tries different types
    of keys (RSA, DSS, ECDSA, Ed25519)."""
    try:
        logger.debug("Attempting to load private key file as RSA key")
        return paramiko.rsakey.RSAKey.from_private_key_file(filename,
            password=password)
    except paramiko.PasswordRequiredException as e:
        raise e
    except Exception as e:
        logger.debug("Cannot load as RSA key: %s" % e)

    try:
        logger.debug("Attempting to load private key file as DSS key")
        return paramiko.dsskey.DSSKey.from_private_key_file(filename,
            password=password)
    except paramiko.PasswordRequiredException as e:
        raise e
    except Exception as e:
        logger.debug("Cannot load as DSS key: %s" % e)

    try:
        logger.debug("Attempting to load private key file as ECDSA key")
        return paramiko.ecdsakey.ECDSAKey.from_private_key_file(filename,
            password=password)
    except paramiko.PasswordRequiredException as e:
        raise e
    except Exception as e:
        logger.debug("Cannot load as ECDSA key: %s" % e)

    try:
        logger.debug("Attempting to load private key file as Ed25519 key")
        return paramiko.ed25519key.Ed25519Key.from_private_key_file(filename,
            password=password)
    except paramiko.PasswordRequiredException as e:
        raise e
    except Exception as e:
        logger.debug("Cannot load as Ed25519 key: %s" % e)

    raise ProjectConfigurationError(
        message="Failed to load private key for SFTP deployment: %s" % filename,
        context=error_context,
    )


def get_host_key(hostname):
    """Helper to look up the host key for the given hostname."""
    try:
        host_keys = paramiko.util.load_host_keys(
            os.path.expanduser("~/.ssh/known_hosts"),
        )
    except IOError as e:
        logger.debug("Unable to open ~/.ssh/known_hosts: %s" % e)
        host_keys = dict()
    return host_keys.get(hostname, None)

