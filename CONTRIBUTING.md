# How to Contribute

We'd love to accept your patches and contributions to this project. There are just a few small guidelines you need to follow.

## Contributor License Agreement

Contributions to this project must be accompanied by a Contributor License
Agreement. You (or your employer) retain the copyright to your contribution,
this simply gives us permission to use and redistribute your contributions as
part of the project. Head over to <https://cla.developers.google.com/> to see
your current agreements on file or to sign a new one.

You generally only need to submit a CLA once, so if you've already submitted one
(even if it was for a different project), you probably don't need to do it
again.

## Code Reviews

All submissions, including submissions by project members, require review. We
use GitHub pull requests for this purpose. Consult
[GitHub Help](https://help.github.com/articles/about-pull-requests/) for more
information on using pull requests.

## Source Code

The comparators in each level are in the `src/comparator` folder, for example: `src/comparator/messageComparator.py `and `src/findings` define the structure of our findings.
The entry point is `src/cli/detect.py`.

## Set Up
1. Clone the repo
2. Copy the Git pre-commit hooks. This will automatically check the code, run tests, and perform linting before each commit.

```.sh
cp .githooks/pre-commit .git/hooks/pre-commit
```

## Running the tool

1. Create and activate a virtual environment

```.sh
python3 -m venv env
source env/bin/activate
```

2. Install the tool in the root directoty

```.sh
python3 -m pip install --editable .
```

3. Run proto-breaking-change-detector

```.sh
proto-breaking-change-detector --help

# Example usage1:
# Detect breaking changes for two versions proto API definition files in test/testdata/protos/enum
proto-breaking-change-detector --original_api_definition_dirs=test/testdata/protos/enum/v1 --update_api_definition_dirs=test/testdata/protos/enum/v1beta1 --original_proto_files=test/testdata/protos/enum/v1/enum_v1.proto --update_proto_files=test/testdata/protos/enum/v1beta1/enum_v1beta1.proto --human_readable_message

# Example usage2:
# Detect breaking changes for two versions of proto API descriptor files.
proto-breaking-change-detector  --original_descriptor_set_file_path=test/testdata/protos/enum/v1/enum_descriptor_set.pb --update_descriptor_set_file_path=test/testdata/protos/enum/v1beta1/enum_descriptor_set.pb --human_readable_message

# Example usage3:
# Detect breaking changes for two versions proto API definition files defined in two directories.
# Custom the output Json file path and output human-readable messages to console.
touch breaking_changes.json

proto-breaking-change-detector \
--original_api_definition_dirs=test/testdata/protos/enum/v1,test/testdata/protos/message/v1 \
--update_api_definition_dirs=test/testdata/protos/enum/v1beta1,test/testdata/protos/message/v1beta1 \
--original_proto_files=test/testdata/protos/enum/v1/enum_v1.proto,test/testdata/protos/message/v1/message_v1.proto \
--update_proto_files=test/testdata/protos/enum/v1beta1/enum_v1beta1.proto,test/testdata/protos/message/v1beta1/message_v1beta1.proto \
--human_readable_message --output_json_path=breaking_changes.json
```

## Unit Tests

A single unit test can be run by this command: 

```sh
python -m unittest test.comparator.test_enum_comparator
```

All unit tests can be run by the following commands, we have all components covered by unit tests: 

```sh
python -m unittest discover test/comparator/
python -m unittest discover test/comparator/wrappers
python -m unittest discover test/detector
python -m unittest discover test/findings
python -m unittest discover test/cli
```

## Format Source Code

The source code can be format by `black` module:

```.sh
# Format source code
python -m black .
# Check without modifying the source code.
python -m black . --check
```
