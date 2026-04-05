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

locals {
  bucket_name = "my-prefix-${var.project_id}"
}

resource "google_storage_bucket" "my_bucket" {
  name     = local.bucket_name
  location = var.region
}