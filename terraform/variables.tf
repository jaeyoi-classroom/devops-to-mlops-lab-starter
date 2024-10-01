# GitHub Actions workflow에서 TF_VAR_github_username으로 환경 변수 설정
variable "github_username" {
  type = string
}

# GitHub Actions workflow에서 TF_VAR_github_token으로 환경 변수 설정
variable "github_token" {
  type      = string
  sensitive = true
}

# GitHub Actions workflow에서 TF_VAR_ghcr_image로 환경 변수 설정
variable "ghcr_image" {
  type = string
}

# GitHub Actions workflow에서 TF_VAR_cluster_name으로 환경 변수 설정
variable "cluster_name" {
  type = string
}

# namespace 이름: hello-kube
variable "namespace" {
  type        = string
  description = "Kubernetes namespace"
  default     = "hello-kube"
}
