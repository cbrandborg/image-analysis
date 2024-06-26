import * as pulumi from "@pulumi/pulumi";
import * as gcp from "@pulumi/gcp";
import { CloudRunDeploymentConfig, ServiceInfo } from './resources/definitions'
import { createServiceAccount } from './resources/service-account'
import { createCloudRunServices } from './resources/cr-services'
import { createStorageBucket } from "./resources/gcs";

const projectId = "interview-demos"
const projectNumber = ""

const imageAnalysisServiceAccount = createServiceAccount(projectId)

const imageAnalysisGCS = createStorageBucket(projectId, "bkt-image-analysis")

const crDeploymentConfig : CloudRunDeploymentConfig = {

    serviceInfo: [
        {
            serviceName: 'image-analysis-service',
            imageUrl: `europe-west1-docker.pkg.dev/interview-demos/cloud-run-docker-demos/neurons-image-analysis-service:v0.1.6`,
            secretEnvVar: 'IMAGE_ANALYSIS_CREDENTIALS',
            secretId: 'image-analysis-service-credentials', 
            cpu: '1',
            memory: '500Mi'
        },
    ],
    projectId: projectId,
    projectNumber: projectNumber,
    region: "europe-west1",
    serviceAccount: imageAnalysisServiceAccount

}

createCloudRunServices(crDeploymentConfig)