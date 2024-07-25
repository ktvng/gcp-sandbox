terraform {
  required_providers {
    google = {
      source = "hashicorp/google"
      version = "5.38.0"
    }
  }
}

variable "project_id" {
  type = string
  default = "moonlit-web-429604-s7"
}

resource "random_id" "differentiator" {
  byte_length = 8
}

variable "location" {
  type = string
  default = "us-west1"
}

provider "google" {
  project = var.project_id
}

// The shared builds bucket
resource "google_storage_bucket" "bucket" {
  name     = "builds-bucket-${var.project_id}"
  location = "US"
  uniform_bucket_level_access = true
  force_destroy = true
}

// The shared build account
resource "google_service_account" "build-account" {
  account_id = "build-account"
  display_name = "build-account"
  description = "Cloudbuild account"
}

resource "google_project_iam_member" "build-account-permissions" {
  project = var.project_id
  member = "serviceAccount:${google_service_account.build-account.email}"
  role = "roles/cloudfunctions.developer"
}

resource "google_project_iam_member" "build-account-logging" {
  project = var.project_id
  member = "serviceAccount:${google_service_account.build-account.email}"
  role = "roles/logging.logWriter"
}

// All funkets
variable "funkets" {
  description = "All microservices following the queue + cloud function pattern"
  type = map(any)

  default = {
    simple-http-function = {
      name = "simple-http-function"
      entry = "simple_http_function"
      public = true
    },
    secondary-function = {
      name = "secondary-function"
      entry = "secondary_function"
    }
  }
}

variable "routes" {
  description = "Map of which funkets can invoke others"
  type = map(any)
  default = {
    simple-http-function = "secondary-function"
  }
}


################################################################################
# VPC
################################################################################
resource "google_compute_network" "backend-vpc" {
  name = "backend-vpc"
  project = var.project_id
  mtu = 1460
  auto_create_subnetworks = false
}

resource "google_vpc_access_connector" "vpc-connector" {
  name = "backend-vpc-connector"
  network = google_compute_network.backend-vpc.name
  ip_cidr_range = "10.1.0.0/28"
  region = var.location
  min_instances = 2
  max_instances = 3
  machine_type = "e2-micro"
}


################################################################################
# Functions
################################################################################

data "archive_file" "local-code" {
  for_each = var.funkets
  type = "zip"
  source_dir = "./src/${each.value.name}/"
  output_path = "./builds/${each.value.name}.zip"
}

resource "google_storage_bucket_object" "cloud-code" {
  for_each = var.funkets
  name = "${each.value.name}.zip"
  bucket = google_storage_bucket.bucket.name
  source = data.archive_file.local-code[each.key].output_path
}

resource "google_service_account" "function-account" {
  for_each = var.funkets
  account_id = "${each.value.name}-account"
  display_name = "${each.value.name}-account"
}

resource "google_cloudfunctions2_function" "cloud-function" {
  for_each = var.funkets
  name = each.value.name
  location = var.location

  build_config {
    runtime = "python312"
    entry_point = each.value.entry
    source {
      storage_source {
        bucket = google_storage_bucket.bucket.name
        object = google_storage_bucket_object.cloud-code[each.key].name
      }
    }
  }
  service_config {
    timeout_seconds = 60
    max_instance_count = 3
    min_instance_count = 0
    service_account_email = google_service_account.function-account[each.key].email
    vpc_connector = google_vpc_access_connector.vpc-connector.name
    ingress_settings = try(each.value["public"], false) ? "ALLOW_ALL" : "ALLOW_INTERNAL_ONLY"
    vpc_connector_egress_settings = "ALL_TRAFFIC"
  }
}

resource "google_project_iam_member" "service-account-users" {
  for_each = var.funkets
  project = var.project_id
  role = "roles/iam.serviceAccountUser"
  member = "serviceAccount:${google_service_account.function-account[each.key].email}"
}

resource "google_cloud_run_service_iam_member" "member" {
  location = google_cloudfunctions2_function.cloud-function["simple-http-function"].location
  service = google_cloudfunctions2_function.cloud-function["simple-http-function"].name
  role     = "roles/run.invoker"
  member   = "user:k.tang1618@gmail.com"
}

resource "google_cloud_run_service_iam_member" "invoker" {
  for_each = var.routes
  location = google_cloudfunctions2_function.cloud-function[each.value].location
  service  = google_cloudfunctions2_function.cloud-function[each.value].name
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.function-account[each.key].email}"
}

resource "google_cloud_tasks_queue" "function-queue" {
  for_each = var.funkets
  location = var.location
  name = "${each.value.name}-queue-${random_id.differentiator.id}"
  project = var.project_id

  rate_limits {
    max_concurrent_dispatches = 2
  }
}

resource "google_cloud_tasks_queue_iam_member" "enqueuer" {
  for_each = var.routes
  location = google_cloudfunctions2_function.cloud-function[each.key].location
  name = google_cloud_tasks_queue.function-queue[each.value].name
  role = "roles/cloudtasks.enqueuer"
  member = "serviceAccount:${google_service_account.function-account[each.key].email}"
}

output "service-config" {
  value = {
    project-id = var.project_id
    deployment-hash = random_id.differentiator.id
    location = var.location
    functions = {
      for k, v in var.funkets:
        k => google_cloudfunctions2_function.cloud-function[k].service_config[0].uri
    }
    queues = {
      for k, v in var.funkets:
        k => google_cloud_tasks_queue.function-queue[k].name
    }
  }
}
