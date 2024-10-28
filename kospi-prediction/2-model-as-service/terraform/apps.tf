# Namespace 정의
resource "kubernetes_namespace" "namespace" {
  metadata {
    name = var.namespace
  }

  depends_on = [
    helm_release.kserve,
  ]
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

# kospi-prediction-app 배포 정보
resource "kubernetes_deployment" "kospi-prediction-app" {
  metadata {
    name      = "kospi-prediction-app-deployment"
    namespace = var.namespace
    labels = {
      app = "kospi-prediction-app"
    }
  }

  spec {
    replicas = 1

    selector {
      match_labels = {
        app = "kospi-prediction-app"
      }
    }

    template {
      metadata {
        labels = {
          app = "kospi-prediction-app"
        }
      }

      spec {
        container {
          image             = var.ghcr_app_image
          name              = "kospi-prediction-app-image"
          image_pull_policy = "IfNotPresent"

          port {
            container_port = 7860
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
  ]
}

# kospi-prediction-app 서비스 정보
resource "kubernetes_service" "kospi-prediction-app" {
  metadata {
    name      = "kospi-prediction-app-service"
    namespace = var.namespace
    labels = {
      app = "kospi-prediction-app"
    }
  }

  spec {
    selector = {
      app = "kospi-prediction-app"
    }

    port {
      port = 7860
    }
  }

  depends_on = [
    kubernetes_namespace.namespace,
    kubernetes_deployment.kospi-prediction-app,
  ]
}

resource "kubectl_manifest" "kospi-prediction-model" {
  yaml_body = <<YAML
apiVersion: serving.kserve.io/v1beta1
kind: InferenceService
metadata:
  name: kospi-prediction-model
  namespace: ${var.namespace}
spec:
  predictor:
    containers:
      - name: kserve-container
        image: ${var.ghcr_model_image}
        imagePullPolicy: "IfNotPresent"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
    imagePullSecrets: 
      - name: ghcr
YAML

  depends_on = [
    kubernetes_namespace.namespace,
    kubernetes_secret.ghcr_secret,
  ]
}
