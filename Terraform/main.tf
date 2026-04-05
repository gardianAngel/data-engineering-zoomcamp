terraform {
  required_version = ">= 1.6.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 5.0"
    }
  }
  backend "local" {
    path = "terraform.tfstate"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Get a temporary token for the service account
data "google_service_account_access_token" "default" {
  provider               = google
  target_service_account = var.service_account_email
  scopes                 = ["https://www.googleapis.com/auth/cloud-platform"]
  lifetime               = "3600s"
}

# Use the temporary token for the impersonated provider
provider "google" {
  alias        = "impersonated"
  access_token = data.google_service_account_access_token.default.access_token
  project      = var.project_id
  region       = var.region
}

locals {
  bucket_name = "my-prefix-${var.project_id}"
}

resource "google_storage_bucket" "my_bucket" {
  provider                      = google.impersonated
  name                          = local.bucket_name
  location                      = var.region
  uniform_bucket_level_access   = true
}