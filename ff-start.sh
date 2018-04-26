# initialize parameters
# identify pull request and push
# prepare upload path, request url

# run Java cmd and store logs
run_script() {
  echo $TRAVIS_BRANCH
  echo $TRAVIS_COMMIT
  echo $TRAVIS_EVENT_TYPE
  echo $TRAVIS_PULL_REQUEST
  echo $TRAVIS_PULL_REQUEST_BRANCH
  echo $TRAVIS_PULL_REQUEST_SHA
  echo $TRAVIS_JDK_VERSION
  mvn depedency:tree
  exit $RESULT
}

run_detect > ./scan/depedency-tree-output.txt
# run script to extrac depedency tree info

# upload to s3 endpoint
