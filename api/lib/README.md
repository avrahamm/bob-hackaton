# jt400.jar goes here — NOT tracked by git
#
# Download command (latest verified: v21.0.7, java11 variant):
#   curl -L "https://github.com/IBM/JTOpen/releases/download/v21.0.7/jt400-21.0.7-java11.jar" \
#        -o api/lib/jt400.jar
#
# Verify after download (~5.2 MB):
#   unzip -l api/lib/jt400.jar | grep AS400JDBCDriver
#   # should show: com/ibm/as400/access/AS400JDBCDriver.class
