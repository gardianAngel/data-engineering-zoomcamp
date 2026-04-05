variable "project_id" {
  type        = string
  description = "GCP Project ID"
  default = "project-5397f083-cbf4-4f3e-9b2"
}

variable "region" {
  type        = string
  description = "GCP Region"
  default     = "us-central1"
}

variable "service_account_email" {
  type        = string
  description = "Service account email for impersonation"
  default     = "terraform-runner@project-5397f083-cbf4-4f3e-9b2.iam.gserviceaccount.com"
}
