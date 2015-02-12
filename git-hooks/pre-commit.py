#!C:\
# pre-commit.py
from git import Repo
import json
import os
import sys
import pdb

print "running pre-commit"
repo_path = os.path.dirname(os.path.realpath(os.path.join(__file__,"..")))
print repo_path
repo = Repo(repo_path)
sha = repo.head.commit.hexsha

index = repo.index
diff_idx = index.diff("HEAD")

print diff_idx
# Traverse added Diff objects only

if diff_idx:
    for diff_added in diff_idx.iter_change_type('M'):
        print(diff_added)

    obj = {'sha':sha}

    ver_path = os.path.join(repo.working_tree_dir, "version.json")
    f = open(ver_path, "w")
    json.dump(obj, f)
    f.close()

    repo.index.add([ver_path])
print "finishing pre-commit"
