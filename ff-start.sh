# initialize parameters
# identify pull request and push
# prepare upload path, request url

# run Java cmd and store logs
run_detect() {
  
  echo "#!/bin/sh" >> $DETECT_JAR_PATH/hub-detect-java.sh
  echo "" >> $DETECT_JAR_PATH/hub-detect-java.sh
  echo $JAVACMD $SCRIPT_ARGS >> $DETECT_JAR_PATH/hub-detect-java.sh
  source $DETECT_JAR_PATH/hub-detect-java.sh
  RESULT=$?
  echo "Result code of ${RESULT}, exiting"
  rm -f $DETECT_JAR_PATH/hub-detect-java.sh
  exit $RESULT
}
# run script to extrac depedency tree info

# upload to s3 endpoint
