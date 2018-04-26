#!/bin/bash
# initialize parameters
# identify pull request and push
# prepare upload path, request url
echo "inside ff-start.sh script"

SCANTIST_IMPORT_URL="http://e8482e5c.ngrok.io/import/"

# run Java cmd and store logs
run_script() {
  echo $TRAVIS_BRANCH
  echo $TRAVIS_COMMIT
  echo $TRAVIS_EVENT_TYPE
  echo $TRAVIS_PULL_REQUEST
  echo $TRAVIS_PULL_REQUEST_BRANCH
  echo $TRAVIS_PULL_REQUEST_SHA
  echo $TRAVIS_JDK_VERSION
  mvn -B dependency:tree
}

run_script > depedency-tree-output.txt
# run script to extrac depedency tree info

# upload to s3 endpoint

#Log that the script download is complete and proceeding
echo "Uploading report at $1"

#Log the curl version used
python --version

curl --version

curl -g -v -f -X POST -d @depedency-tree-output.txt -H 'Content-Type:application/json' "$SCANTIST_IMPORT_URL"

#Exit with the curl command's output status
exit $?
