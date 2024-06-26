import * as fs from 'fs';
import * as pulumi from "@pulumi/pulumi";
import * as gcp from "@pulumi/gcp";
import { CloudRunDeploymentConfig } from './definitions'

export async function createCloudRunServices( crDeploymentConfig: CloudRunDeploymentConfig ) {


    crDeploymentConfig.serviceInfo.forEach(serviceInfo => {

        const parent = new pulumi.ComponentResource(
            `neurons:cloudRun:${serviceInfo.serviceName}`,
            serviceInfo.serviceName,
        );

        const secretAccessorIamMember = new gcp.secretmanager.SecretIamMember(`secretAccessorMember${serviceInfo.serviceName}`, {
            project: crDeploymentConfig.projectId,
            secretId: serviceInfo.secretId,
            role: "roles/secretmanager.secretAccessor",
            member: crDeploymentConfig.serviceAccount.email.apply(email => `serviceAccount:${email}`),
        }, { parent, dependsOn: [crDeploymentConfig.serviceAccount ] });



        // Create a new Cloud Run service for each serviceInfo
        const cloudRunService = new gcp.cloudrunv2.Service(
            `cr-${serviceInfo.serviceName}`,
            {
                project: crDeploymentConfig.projectId,
                location: crDeploymentConfig.region,
                ingress: "INGRESS_TRAFFIC_ALL",
                template: {
                    serviceAccount: crDeploymentConfig.serviceAccount.email,
                    timeout: "3600s",
                    maxInstanceRequestConcurrency: 1,
                    scaling: {
                        maxInstanceCount: 25,
                    },
                    containers: [{
                        image: serviceInfo.imageUrl,
                        resources: {
                            cpuIdle: true,
                            limits: {
                                cpu: serviceInfo.cpu,
                                memory: serviceInfo.memory,
                            },
                        },
                        envs: [{
                            name: serviceInfo.secretEnvVar,
                            valueSource: {
                                secretKeyRef: {
                                    secret: serviceInfo.secretId,
                                    version: 'latest'
                                }
                            }
                        }],
                    }],
                },
            }, { parent, dependsOn: [crDeploymentConfig.serviceAccount, secretAccessorIamMember] });

        const invokerAllUsers = new gcp.cloudrun.IamMember("invoker", {
            service: cloudRunService.name,
            location: cloudRunService.location,
            project: cloudRunService.project,
            role: "roles/run.invoker",
            member: "allUsers",
        }, { parent, dependsOn: [crDeploymentConfig.serviceAccount, secretAccessorIamMember, cloudRunService]});

    //////// Cloud Run IAM ////////
    const crInvokerIam = new gcp.cloudrunv2.ServiceIamMember(`crInvokerIamMember${serviceInfo.serviceName}`, {
        project: cloudRunService.project,
        name: cloudRunService.name,
        location: "europe-west1",
        role: "roles/run.invoker",
        member: crDeploymentConfig.serviceAccount.email.apply(email => `serviceAccount:${email}`),

    }, { parent, dependsOn: [cloudRunService] });

    const storageObjectReaderIamMember = new gcp.projects.IAMMember(`storageObjectReaderIamMember${serviceInfo.serviceName}`, {
        project: cloudRunService.project,
        role: "roles/storage.objectUser",
        member: crDeploymentConfig.serviceAccount.email.apply(email => `serviceAccount:${email}`),

    }, { parent, dependsOn: [cloudRunService] });

    const storageInsightsCollectorIamMember = new gcp.projects.IAMMember(`storageInsightsCollectorIamMember${serviceInfo.serviceName}`, {
        project: cloudRunService.project,
        role: "roles/storage.insightsCollectorService",
        member: crDeploymentConfig.serviceAccount.email.apply(email => `serviceAccount:${email}`),

    }, { parent, dependsOn: [cloudRunService] });
    
    })
}