# Test -- only after stack already exists
pytest app/Tests/test_contacts.py
# Stop the pipeline if the python script fails (exit code 1)
if [[ $? -eq 1 ]]; then
  exit 1
fi

#  Building Artifacts directory
BUILD_DIR=artifacts/build-$BUILD_NUM
mkdir -p $BUILD_DIR

# Create the environment
DIR=$(pwd)
pipenv install
SITE_PACKAGES=$(pipenv --venv)/lib/python3.9/site-packages

# Get the environment files and zip them
LAYER=python/lib/python3.9/site-packages
mkdir -p $BUILD_DIR/$LAYER
cd $SITE_PACKAGES
cp -r * $DIR/$BUILD_DIR/$LAYER
cd $DIR/$BUILD_DIR
zip -r9 api_layer.zip python
rm -rf python
cd $DIR

# Zip the api itself
cd app && zip -r9 api.zip . && cd ..
cp app/api.zip $BUILD_DIR
rm app/api.zip

cp Templates/cloudformation.yml $BUILD_DIR

#  Make the bucket if not exists
aws s3 mb s3://${S3BUCKET} --region $AWSREGION

# Make Sure that public access is blocked
aws s3api put-public-access-block \
    --bucket "${S3BUCKET}" \
    --public-access-block-configuration "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"

#  Uploading build to s3
aws s3 sync artifacts s3://${S3BUCKET}

#  Running Stack create or update
python3 Deployment/deploy.py
