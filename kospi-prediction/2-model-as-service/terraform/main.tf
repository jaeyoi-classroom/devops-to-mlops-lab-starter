terraform {
  backend "local" {
    path = "../../../../terraform.tfstate"
  }

  required_providers {
    kubectl = {
      source  = "alekc/kubectl"
      version = "~> 2.0"
    }
  }
}

provider "kubernetes" {
  config_path = "~/.kube/config"
}
