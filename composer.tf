provider "google" {
  project = "unifycare-424906"
}

variable "project_id" {
  type = string
  description = "The Google Cloud project ID"
  default = "unifycare-424906"
}

resource "google_service_account" "test" {
  account_id   = "composer-env-account-new"
  display_name = "Test Service Account for Composer Environment"
}

resource "google_project_iam_member" "composer_worker" {
  project = var.project_id
  role    = "roles/composer.worker"
  member  = "serviceAccount:composer-env-account-new@${var.project_id}.iam.gserviceaccount.com"
}

resource "google_project_iam_member" "composer_service_agent" {
  project = var.project_id
  role    = "roles/composer.serviceAgent"
  member  = "serviceAccount:composer-env-account-new@${var.project_id}.iam.gserviceaccount.com"
}

resource "google_project_iam_member" "composer_service_agent_V2Ext" {
  project = var.project_id
  role    = "roles/composer.ServiceAgentV2Ext"
  member  = "serviceAccount:composer-env-account-new@${var.project_id}.iam.gserviceaccount.com"
}






resource "google_composer_environment" "test" {
  name   = "example-composer-env-tf-c2"
  region = "us-central1"
  
  config {
    software_config {
      image_version = "composer-2-airflow-2"
    }

    workloads_config {
      scheduler {
        count      = 2
        cpu        = 1
        memory_gb  = 2
        storage_gb = 1
      }
      web_server {
        cpu        = 0.5
        memory_gb  = 2
        storage_gb = 1
      }
      triggerer {
        cpu        = 0.5
        memory_gb  = 0.5
        count      = 2
      }
      worker {
        cpu        = 4
        memory_gb  = 8
        storage_gb = 4
        min_count  = 8
        max_count  = 16
      }
    }

    environment_size = "ENVIRONMENT_SIZE_MEDIUM"

    private_environment_config {
      enable_private_endpoint = true
      
    }

    node_config {
      network          = "default"
      subnetwork       = "default"
      service_account  =  "composer-env-account@unifycare-424906.iam.gserviceaccount.com"
      # ip_allocation_policy {
      #   cluster_secondary_range_name  = "var.subnetwork_pod_range_name"
      #   services_secondary_range_name = "var.subnetwork_svc_range_name"
      # }  
    }

  }
}






