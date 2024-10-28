variable "github_username" {
  type = string
}

variable "github_token" {
  type      = string
  sensitive = true
}

variable "ghcr_app_image" {
  type = string
}

variable "ghcr_model_image" {
  type = string
}

variable "namespace" {
  type        = string
  description = "Kubernetes namespace"
}
