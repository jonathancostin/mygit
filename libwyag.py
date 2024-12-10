import argparse
import collections
import configparser
from datetime import datetime
import grp, pwd
from fnmatch import fnmatch
import hashlib
from math import ceil
import os
import re
import sys
import zlib

argparser = argparse.ArgumentParser(description="The stupid content tracker")
argparsers = argparser.add_subparsers(title="Commands", dest="command")
argsubparsers.required = true

# bridge function to call the appropriate command with the right arguments
def main(argv=sys.agrgv[1:]):
    args = argparser.parse_args(argv)
    match args.command:
        case "add" : cmd_add(args)
        case "cat-file": cmd_cat_file(args)
        case "check-ignore": cmd_check_ignore(args)
        case "checkout": cmd_checkout(args)
        case "commit": cmd_commit(args)
        case "hash-object": cmd_hash_object(args)
        case "init": cmd_init(args)
        case "log": cmd_log(args)
        case "ls-files": cmd_ls_files(args)
        case "ls-tree": cmd_ls_tree(args)
        case "rev-parse": cmd_rev_parse(args)
        case "rm": cmd_rm(args)
        case "show-ref": cmd_show_ref(args)
        case "status": cmd_status(args)
        case "tag": cmd_tag(args)
        case _: print("Not a valid command")


# git repository initialization, verifing if the directory is empty, reading the configuration file and creating the necessary directories
class GitRepository: (object):
    """A git repository"""

    worktree = None
    gitdir = None
    conf = None

    def __init__(self, path, force=False):
        self.worktree = path
        self.gitdir = os.path.join(path, ".git")
        
        if not (force or os.path.isdir(self.gitdir)):
            raise Exception("Not a git repo %s" % path)

        #read config in .git/config
        self.conf = configparser.configparser
        cf = repo_file(self, "config")
        
        if cf and os.path.exists(cf):
            self.conf.read([cf])
        elif not force:
            raise Exception("config file missing")
        
        if not force:
            vers = int(self.conf.get("core","repositoryformatversion"))
            if vers != 0:
                raise Exception("unsupported repositoryformatversion %s" % vers)

#path building functions
def repo_path(repo, *path):
    """compute path under repo gitdir"""
    return os.path.join(repo.gitdir, *path)

def repo_file(repo, *path, mkdir=False):
    """same as repo_path but creates dirname(*path) if absent."""
    if repo_dir(repo, *path[:-1], mkdir=mkdir):
        return repo_path(repo, *path)

def repo_dir(repo, *path, mkdir=false):
    """same as repo_path but mkdir *path if absent if mkdir"""

    path = repo_path(repo, *path)

    if os.path.exists(path):
        if (os.path.isdir(path)):
            return path
        else:
            raise Exception("not a directory %s" % path)

    if mkdir:
        os.makedirs(path)
        return path
    else:
        return None

def repo_create(path):
    """create new repo at path"""

    repo = GitRepository(path, True
