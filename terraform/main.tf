terraform {
  # terraform으로 minikube를 관리하기 위한 provider
  required_providers {
    minikube = {
      source  = "scott-the-programmer/minikube"
    }
  }
}

provider "minikube" {
  kubernetes_version = "v1.30.0"
}

# minikube cluster를 docker 기반으로 생성
resource "minikube_cluster" "docker" {
  driver       = "docker"
  cluster_name = var.cluster_name
  addons = [
    "default-storageclass",
    "storage-provisioner",
    "dashboard"
  ]
}

provider "kubernetes" {
  host = minikube_cluster.docker.host

  client_certificate     = minikube_cluster.docker.client_certificate
  client_key             = minikube_cluster.docker.client_key
  cluster_ca_certificate = minikube_cluster.docker.cluster_ca_certificate
}

# Namespace 정의
resource "kubernetes_namespace" "namespace" {
  metadata {
    name = var.namespace
  }
}

# GitHub Container Registry에 접근하기 위한 시크릿 정보 
resource "kubernetes_secret" "ghcr_secret" {
  metadata {
    name      = "ghcr"
    namespace = var.namespace
  }

  data = {
    ".dockerconfigjson" = jsonencode({
      "auths" = {
        "ghcr.io" = {
          "username" = var.github_username
          "password" = var.github_token
          "auth"     = base64encode("${var.github_username}:${var.github_token}")
        }
      }
    })
  }

  type = "kubernetes.io/dockerconfigjson"

  depends_on = [ 
    kubernetes_namespace.namespace
  ]
}

# hello api server 배포 정보
resource "kubernetes_deployment" "api" {
  metadata {
    name      = "api-deployment"
    namespace = var.namespace
    labels = {
      app = "api"
    }
  }

  spec {
    replicas = 1

    selector {
      match_labels = {
        app = "api"
      }
    }

    template {
      metadata {
        labels = {
          app = "api"
        }
      }

      spec {
        container {
          image             = var.ghcr_image
          name              = "labs-image"
          image_pull_policy = "Always"

          port {
            container_port = 5000
          }
        }

        image_pull_secrets {
          name = "ghcr"
        }
      }
    }
  }

  depends_on = [
    kubernetes_namespace.namespace,
    kubernetes_secret.ghcr_secret,
    kubernetes_service.db,
  ]
}

# hello api server 서비스 정보
resource "kubernetes_service" "api" {
  metadata {
    name      = "api-service"
    namespace = var.namespace
    labels = {
      app = "api"
    }
  }

  spec {
    type = "NodePort"

    selector = {
      app = "api"
    }

    port {
      port        = 5000
      target_port = 5000
      node_port   = 30000
    }
  }

  depends_on = [
    kubernetes_namespace.namespace,
    kubernetes_deployment.api,
  ]
}

# db server 배포 정보
resource "kubernetes_deployment" "db" {
  metadata {
    name      = "db-deployment"
    namespace = var.namespace
    labels = {
      app = "postgres"
    }
  }

  spec {
    replicas = 1

    selector {
      match_labels = {
        app = "postgres"
      }
    }

    template {
      metadata {
        labels = {
          app = "postgres"
        }
      }

      spec {
        container {
          name  = "postgres"
          image = "postgres:16"

          port {
            container_port = 5432
          }

          env {
            name  = "POSTGRES_PASSWORD"
            value = "mysecretpassword"
          }

          volume_mount {
            name       = "db-data"
            mount_path = "/var/lib/postgresql/data"
          }
        }

        volume {
          name = "db-data"

          persistent_volume_claim {
            claim_name = "db-data-pvc"
          }
        }
      }
    }
  }

  depends_on = [
    kubernetes_namespace.namespace,
    kubernetes_persistent_volume_claim.db_data
  ]
}

# db server 서비스 정보
resource "kubernetes_service" "db" {
  metadata {
    name      = "db"
    namespace = var.namespace
  }

  spec {
    type = "ClusterIP"

    selector = {
      app = "postgres"
    }

    port {
      port        = 5432
      target_port = 5432
    }
  }

  depends_on = [
    kubernetes_namespace.namespace,
    kubernetes_deployment.db,
  ]
}

# db server에서 사용할 볼륨 정보
resource "kubernetes_persistent_volume_claim" "db_data" {
  metadata {
    name      = "db-data-pvc"
    namespace = var.namespace
  }

  spec {
    access_modes = ["ReadWriteOnce"]

    resources {
      requests = {
        storage = "1Gi"
      }
    }
  }

  depends_on = [
    kubernetes_namespace.namespace,
  ]
}
