#!/bin/bash
# initialize parameters
# identify pull request and push
# prepare upload path, request url
echo "inside ff-start.sh script"

SCANTIST_IMPORT_URL="http://e8482e5c.ngrok.io/import/"

show_project_info() {
  echo "TRAVIS_EVENT_TYPE $TRAVIS_EVENT_TYPE"
  echo "TRAVIS_BRANCH $TRAVIS_BRANCH"
  echo "TRAVIS_REPO_SLUG $TRAVIS_REPO_SLUG"
  echo "TRAVIS_PULL_REQUEST_SLUG $TRAVIS_PULL_REQUEST_SLUG"
  echo "TRAVIS_PULL_REQUEST $TRAVIS_PULL_REQUEST"
  echo "TRAVIS_PULL_REQUEST_BRANCH $TRAVIS_PULL_REQUEST_BRANCH"
  echo "TRAVIS_PULL_REQUEST_SHA $TRAVIS_PULL_REQUEST_SHA"
  echo "TRAVIS_COMMIT $TRAVIS_COMMIT"
  echo "=================project info====================="
}
echo "=================show_project_info================="
show_project_info

repo_name=$TRAVIS_REPO_SLUG
commit_sha=$TRAVIS_COMMIT
branch=$TRAVIS_BRANCH
pull_request=$TRAVIS_PULL_REQUEST
build_time=$(date +"%s")

ls

cwd=$(pwd)
echo $cwd

pyenv versions

pyenv global 3.6.3

python TreeBuilder.py $cwd $repo_name $commit_sha $branch $pull_request $build_time

#Log that the script download is complete and proceeding
echo "Uploading report at $SCANTIST_IMPORT_URL"

#Log the curl version used
curl --version

curl -g -v -f -X POST -d '@dependency-tree.json' -H 'Content-Type:application/json' "$SCANTIST_IMPORT_URL"

#Exit with the curl command's output status
exit $?
