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

provider "google" {
  project = var.project_id
}

resource "google_storage_bucket" "bucket" {
  name     = "builds-bucket-${var.project_id}"
  location = "US"
  uniform_bucket_level_access = true
  force_destroy = true
}

data "archive_file" "simple_http_function_zip" {
  type        = "zip"
  output_path = "./builds/simple_http_function.zip"
  source_dir  = "simple_http_function/"
}

resource "google_storage_bucket_object" "simple_http_function_code" {
  name   = "simple_http_function_code.zip"
  bucket = google_storage_bucket.bucket.name
  source = data.archive_file.simple_http_function_zip.output_path
}

resource "google_cloudfunctions2_function" "simple_http_function" {
  name = "simple-http-function"
  location = "us-west1"

  build_config {
    runtime = "python312"
    entry_point = "entry"

    source {
      storage_source {
        bucket = google_storage_bucket.bucket.name
        object = google_storage_bucket_object.simple_http_function_code.name
      }
    }
  }

  service_config {
    timeout_seconds = 60
    max_instance_count = 1
  }
}

resource "google_cloud_run_service_iam_member" "member" {
  location = google_cloudfunctions2_function.simple_http_function.location
  service  = google_cloudfunctions2_function.simple_http_function.name
  role     = "roles/run.invoker"
  member   = "user:k.tang1618@gmail.com"
}

resource "google_service_account" "build_account" {
  account_id = "build-account"
  display_name = "build-account"
  description = "Cloudbuild account"
}

resource "google_cloudbuild_trigger" "build-trigger" {
  location = "us-central1"

  repository_event_config {
    repository = "ktvng-gcp-sandbox"
    push {
      branch = "main"
    }
  }

  filename = "cloudbuild.yaml"
}

output "function_uri" {
  value = google_cloudfunctions2_function.simple_http_function.service_config[0].uri
}
