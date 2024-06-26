import * as pulumi from "@pulumi/pulumi";
import * as gcp from "@pulumi/gcp";

export async function createStorageBucket(projectId: string, name: string) {
    const bucket = new gcp.storage.Bucket("bkt-image-analysis", {
        project: projectId,
        name: name,
        location: "europe-west1",
        forceDestroy: true,
        uniformBucketLevelAccess: true, 
        storageClass: "STANDARD",
    });

    return bucket
}