#!/bin/bash
# initialize parameters
# identify pull request and push
# prepare upload path, request url
echo "inside ff-start.sh script"

SCANTIST_IMPORT_URL="http://e8482e5c.ngrok.io/import/"


# # run Java cmd and store logs
# run_script() {
#   if [ -f pom.xml ]; then
#     mvn -B dependency:tree
#   fi
#   if [ -f build.gradle ]; then
#     gradle dependencies --configuration compile
#   fi

# }
# echo "------------------------------------"
# echo "run_script"

# run_script > raw-output.txt

# run script to extrac depedency tree info
chmod a+x TreeBuilder
cwd=$(pwd)
ls
echo $cwd
./TreeBuilder $cwd

cat raw-output.txt

#Log that the script download is complete and proceeding
echo "Uploading report at $SCANTIST_IMPORT_URL"

#Log the curl version used
python3 --version

curl --version

curl -g -v -f -X POST -d '@dependency-tree.json' -H 'Content-Type:application/json' "$SCANTIST_IMPORT_URL"

#Exit with the curl command's output status
exit $?
