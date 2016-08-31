import json
import os

import conda_build.metadata
import conda_smithy.feedstocks

import argparse

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument("--feedstocks-directory", default="./")
parser.add_argument("--json-output", default="dependencies.json")
args = parser.parse_args()

deps = {}
for feedstock in conda_smithy.feedstocks.cloned_feedstocks(args.feedstocks_directory):
    try:
        meta = conda_build.metadata.MetaData(os.path.join(feedstock.directory, 'recipe'))
    except AssertionError:
        continue

    for spec in meta.ms_depends('run'):
        deps.setdefault(spec.name, []).append(meta.name())


with open(args.json_output, 'w') as fh:
    json.dump(deps, fh, sort_keys=True, indent=4)




