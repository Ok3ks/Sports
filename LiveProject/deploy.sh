docker build . -t $IMAGE_NAME:$REVISION

docker tag $IMAGE_NAME:$REVISION $REGION-docker.pkg.dev/$PROJECT_NAME/$ARTIFACT_REPO_NAME/$IMAGE_NAME:$REVISION

pack build --builder=gcr.io/buildpacks/builder $REGION-docker.pkg.dev/$PROJECT_NAME/$ARTIFACT_REPO_NAME/$IMAGE_NAME:$REVISION --env GOOGLE_PYTHON_VERSION=3.12.4

echo "pushing $REGION-docker.pkg.dev/$PROJECT_NAME/$ARTIFACT_REPO_NAME/$IMAGE_NAME:$REVISION to Artifacts Registry"

docker push $REGION-docker.pkg.dev/$PROJECT_NAME/$ARTIFACT_REPO_NAME/$IMAGE_NAME:$REVISION

echo "Image pushed"

