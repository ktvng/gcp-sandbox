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
resource "google_service_account" "build_account" {
  account_id = "build-account"
  display_name = "build-account"
  description = "Cloudbuild account"
}

// All funkets
variable "funkets" {
  description = "All microservices following the queue + cloud function pattern"
  type = map(any)

  default = {
    simple-http-function = {
      name = "simple-http-function"
    },
    secondary-function = {
      name = "secondary-function"
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

data "archive_file" "local-code" {
  for_each = var.funkets
  type = "zip"
  source_dir = "./${each.value.name}/"
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
    entry_point = "entry"
    source {
      storage_source {
        bucket = google_storage_bucket.bucket.name
        object = google_storage_bucket_object.cloud-code[each.key].name
      }
    }
  }
  service_config {
    timeout_seconds = 60
    max_instance_count = 1
    service_account_email = google_service_account.function-account[each.key].email
  }
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

resource "google_cloud_tasks_queue_iam_member" "creator" {
  for_each = var.routes
  location = google_cloudfunctions2_function.cloud-function[each.key].location
  name = "test-task-queue"
  role = "roles/cloudtasks.enqueuer"
  member = "serviceAccount:${google_service_account.function-account[each.key].email}"
}

resource "google_cloud_tasks_queue" "function-queue" {
  for_each = var.funkets
  location = var.location
  name = "${each.value.name}-queue"
}

resource "google_cloud_tasks_queue_iam_member" "enqueuer" {
  for_each = var.routes
  location = google_cloudfunctions2_function.cloud-function[each.key].location
  name = google_cloud_tasks_queue.function-queue[each.value].name
  role = "roles/cloudtasks.enqueuer"
  member = "serviceAccount:${google_service_account.function-account[each.key].email}"
}

resource "google_cloud_tasks_queue" "task-queue" {
  location = "us-west1"
  name = "test-task-queue"
}

output "function-uris" {
  value = {
    for k, v in var.funkets :
      k => google_cloudfunctions2_function.cloud-function[k].service_config[0].uri
  }
}

output "queue-names" {
  value = {
    for k, v in var.funkets :
      k => google_cloud_tasks_queue.function-queue[k].name
  }
}
