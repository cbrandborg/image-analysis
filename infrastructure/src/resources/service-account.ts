import * as pulumi from "@pulumi/pulumi";
import * as gcp from "@pulumi/gcp";

export function createServiceAccount(projectId: any) {

    const serviceAccountImageAnalysis = new gcp.serviceaccount.Account(`serviceAccount-image-analysis`, {
        accountId:          `sa-image-analysis`,
        displayName:        "Service Account for Image analysis",
        project:            projectId
    }, );

    return serviceAccountImageAnalysis

}