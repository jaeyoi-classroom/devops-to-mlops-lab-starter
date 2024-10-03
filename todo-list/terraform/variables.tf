variable "github_username" {
  type = string
}

variable "github_token" {
  type      = string
  sensitive = true
}

variable "ghcr_frontend_image" {
  type = string
}

variable "ghcr_backend_image" {
  type = string
}

variable "cluster_name" {
  type = string
}

variable "namespace" {
  type        = string
  description = "Kubernetes namespace"
}