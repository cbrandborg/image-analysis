import * as pulumi from "@pulumi/pulumi";
import * as gcp from "@pulumi/gcp";

export interface ServiceInfo {
    serviceName:            string;
    imageUrl:               string;
    secretEnvVar:           string;
    secretId:               string;
    cpu:                    string;
    memory:                 string;

}

export interface CloudRunDeploymentConfig {

    serviceInfo:              ServiceInfo[];
    projectId:              any;  // specify the type
    projectNumber:          any;  // specify the type
    region:                 any;
    serviceAccount:         gcp.serviceaccount.Account;
}