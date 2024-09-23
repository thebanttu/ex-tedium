#!/usr/bin/env python3

from pprint import pprint as pp
import errno
import functools
import importlib.util as iu
import os
import os.path
import re
import signal
import socket
import subprocess
import sys
import time

class TimeoutError(Exception):
    pass

class marangi:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class bantu_utils:
    @staticmethod
    def is_installed(p):
        """Acknowledgement:
        https://stackoverflow.com/questions/1051254/check-if-python-package-is-installed
        """
        spec = iu.find_spec(p)
        if spec is None:
            return False
        return True

    @staticmethod
    def install(p):
        __class__.internet()
        cmd = [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--break-system-packages",
            "--user",
            "--upgrade",
            p,
        ]
        subprocess.check_call(cmd)

    @staticmethod
    def my_import(p):
        if not __class__.is_installed(p):
            __class__.install(p)
        module = iu.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        return

    @staticmethod
    def is_dir_empty(d):
        d = os.path.expanduser(d)
        if os.path.isdir(d):
            return not bool(os.listdir(d))
        return False

    @staticmethod
    def cmd_internet(host="8.8.8.8", port=53, timeout=3):
        """
        Host: 8.8.8.8 (google-public-dns-a.google.com)
        OpenPort: 53/tcp
        Service: domain (DNS/TCP)
        """
        try:
            socket.setdefaulttimeout(timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
            return True
        except socket.error as ex:
            print("No Internet :(")
            return False

    @staticmethod
    def internet(host="8.8.8.8", port=53, timeout=3, msg=None):
        """
        Host: 8.8.8.8 (google-public-dns-a.google.com)
        OpenPort: 53/tcp
        Service: domain (DNS/TCP)
        """
        try:
            socket.setdefaulttimeout(timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
            return True
        except socket.error as ex:
            if msg:
                print(msg)
                return False
            else:
                print("No internet, sort that out first.")
            sys.exit(10)

    @staticmethod
    def handle_ctrl_c(s, f):
        print("\rCTRL C pressed. Proceeding to exit...")
        sys.exit(3)

    @staticmethod
    def amiroot():
        if os.getuid() == 0:
            return True
        else:
            print("Insufficient privileges cannot continue :(")
            sys.exit(5)

    @staticmethod
    def make_rsync_includes(i=[]):
        include_list = []
        for include in i:
            include_list.append('--files-from=' + include)
        include_list.append("--exclude='*'")
        return include_list

    @staticmethod
    def make_rsync_excludes(e=[]):
        exclude_list = []
        for exclude in e:
            exclude_list.append('--exclude-from=' + exclude)
        return exclude_list

    @staticmethod
    def fetch(s, d, **kwargs):
        """Do not delete, strictly!"""
        prefix_1 = "Syncing"
        prefix_2 = "with"
        cmd = [
            'rsync',
            '--partial',
            '--progress',
            '--human-readable',
            '--archive',
            '--verbose',
        ]
        if 'inc' in kwargs:
            include = __class__.make_rsync_includes(kwargs['inc'])
            cmd += include
        if 'ex' in kwargs:
            exclude = __class__.make_rsync_excludes(kwargs['ex'])
            cmd += exclude
        if type(s) is list:
            cmd += s
            prefix_1 = "Sending"
            prefix_2 = "to"
        else:
            cmd.append(s)
        cmd.append(d)
        print(f"{prefix_1} {marangi.OKBLUE}{s}{marangi.ENDC} "
              f"{prefix_2} {marangi.OKGREEN}{d}{marangi.ENDC}")
        #print(f"Running rsync command -> {' '.join(cmd)}")
        r = subprocess.run(cmd, capture_output=False,
                           universal_newlines=True,
                           check=True)
        return r.returncode == 0

    @staticmethod
    def xrsync(s, d, **kwargs):
        prefix_1 = "Syncing"
        prefix_2 = "with"
        cmd = [
            'rsync',
            '--partial',
            '--progress',
            '--human-readable',
            '--archive',
            '--no-g',
            '--no-p',
            '--no-o',
            '--no-acls',
            # '--delete',
            # '--delete-excluded',
            #'--verbose',
        ]
        if 'inc' in kwargs:
            include = __class__.make_rsync_includes(kwargs['inc'])
            cmd += include
        if 'ex' in kwargs:
            exclude = __class__.make_rsync_excludes(kwargs['ex'])
            cmd += exclude
        if 'dry' in kwargs:
            cmd += [ "--dry-run" ]
        if type(s) is list:
            cmd += s
            prefix_1 = "Sending"
            prefix_2 = "to"
        else:
            cmd.append(s)
        cmd.append(d)
        print(f"{prefix_1} {marangi.OKBLUE}{s}{marangi.ENDC} "
              f"{prefix_2} {marangi.OKGREEN}{d}{marangi.ENDC}")
        #print(f"Running rsync command -> {' '.join(cmd)}")
        r = subprocess.run(cmd, capture_output=False,
                           universal_newlines=True,
                           check=False)
        return r.returncode == 0

    @staticmethod
    def bantu_cpio(s, d, e=None):
        """
        The 3rd argument is just to make sure
        the method's signature matches that of
        bantu_rsync to reduce headaches
        """
        s = re.sub(r' ', "\n", s)
        cmd = [
            'cpio',
            '-pmdv',
        ]
        cmd.append(d)
        print(f"Copying {s} to {d}")
        print(f"Running cpio command -> {' '.join(cmd)}")
        r = subprocess.run(cmd, capture_output=False,
                           universal_newlines=True,
                           input=s, check=True)
        return r.returncode == 0

    @staticmethod
    def restart_if():
        cmd_wpa_supp = ['/usr/bin/sudo', '/usr/bin/sv', 'wpa_supplicant', 'restart']
        cmd_dhcpcd = ['/usr/bin/sudo', '/usr/bin/sv', 'dhcpcd', 'restart']
        print('Restarting the network...')
        subprocess.run(cmd_wpa_supp, capture_output=True)
        subprocess.run(cmd_dhcpcd, capture_output=True)
        return

    @staticmethod
    def check_internet(w=25):
        def resume(s, f):
            print("Resuming internet check...")
            signal.raise_signal(signal.SIGCONT)
        c = 1
        signal.signal(signal.SIGALRM, resume)
        while not __class__.cmd_internet():
            time.sleep(2)
            if c > 0 and c % 5 == 0:
                signal.alarm(w)
                print(f"Waiting {w} seconds before trying again...")
                signal.pause()
                #__class__.restart_if()
            c = c + 1
        print("You are ONLINE")

    @staticmethod
    def timeout(seconds=10, msg=os.strerror(errno.ETIME)):
        def decorator(func):
            def _handle_timeout(signum, frame):
                raise TimeoutError(msg)
            @functools.wraps(func)
            def wrapper(self, *args, **kwargs):
                signal.signal(signal.SIGALRM, _handle_timeout)
                signal.alarm(seconds)
                try:
                    result = func(self, *args, **kwargs)
                finally:
                    signal.alarm(0)
                return result
            return wrapper
        return decorator

    @staticmethod
    def ensure_excludes_dir_is_present():
        d = os.path.expanduser('~/.excludes')
        if not os.path.exists(d):
            os.mkdir(d)

    @staticmethod
    def does_file_exist_remotely(p, h='zeus'):
        if len(p) == 0:
            return False
        prefixes = [
            '.downloads/'
        ]
        for prefix in prefixes:
            cmd = [
                'ssh',
                h,
                '--',
                'shopt',
                '-s',
                'nocaseglob;',
                'ls',
                '-d',
            ]
            p = [ prefix + "*" + item + "*" for item in p ]
            cmd += p
            r = subprocess.run(cmd, capture_output=False,
                               universal_newlines=True,
                               check=False)
            returns.append(r)
            final_return = False
            for rr in returns:
                final_return = r.returncode == 0
            return final_return


signal.signal(signal.SIGINT, bantu_utils.handle_ctrl_c)
