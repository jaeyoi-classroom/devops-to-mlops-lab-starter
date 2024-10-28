provider "helm" {
  kubernetes {
    config_path = "~/.kube/config"
  }
}

variable "istio_version" {
  type    = string
  default = "1.23.2"
}

variable "knative_operator_version" {
  type    = string
  default = "v1.15.7"
}

variable "knative_serving_version" {
  type    = string
  default = "1.15.2"
}

variable "cert_manager_version" {
  type    = string
  default = "1.16.1"
}

variable "kserve_version" {
  type    = string
  default = "v0.14.0"
}

resource "helm_release" "istio-base" {
  name             = "istio-base"
  chart            = "base"
  namespace        = "istio-system"
  version          = var.istio_version
  repository       = "https://istio-release.storage.googleapis.com/charts"
  create_namespace = true
  upgrade_install  = true

  set {
    name  = "defaultRevision"
    value = "default"
  }
}

resource "helm_release" "istiod" {
  name             = "istiod"
  chart            = "istiod"
  namespace        = "istio-system"
  version          = var.istio_version
  repository       = "https://istio-release.storage.googleapis.com/charts"
  create_namespace = true
  upgrade_install  = true

  set {
    name  = "proxy.autoInject"
    value = "disabled"
  }

  set {
    name  = "pilot.podAnnotations.cluster-autoscaler\\.kubernetes\\.io/safe-to-evict"
    value = "true"
    type  = "string"
  }

  depends_on = [
    helm_release.istio-base,
  ]
}

resource "helm_release" "istio-ingressgateway" {
  name             = "istio-ingressgateway"
  chart            = "gateway"
  namespace        = "istio-system"
  version          = var.istio_version
  repository       = "https://istio-release.storage.googleapis.com/charts"
  create_namespace = true
  wait             = false
  upgrade_install  = true

  set {
    name  = "pilot.podAnnotations.cluster-autoscaler\\.kubernetes\\.io/safe-to-evict"
    value = "true"
    type  = "string"
  }

  provisioner "local-exec" {
    command = "kubectl wait --for=condition=Ready pod -l app=istio-ingressgateway -n istio-system --timeout=600s"
  }

  depends_on = [
    helm_release.istiod,
  ]
}

resource "helm_release" "cert-manager" {
  name             = "cert-manager"
  chart            = "cert-manager"
  namespace        = "cert-manager"
  version          = var.cert_manager_version
  repository       = "https://charts.jetstack.io"
  create_namespace = true
  upgrade_install  = true

  set {
    name  = "crds.enabled"
    value = "true"
  }

  depends_on = [
    helm_release.istio-ingressgateway,
  ]
}

resource "helm_release" "knative-operator" {
  name             = "knative-operator"
  chart            = "https://github.com/knative/operator/releases/download/knative-${var.knative_operator_version}/knative-operator-${var.knative_operator_version}.tgz"
  namespace        = "knative-serving"
  create_namespace = true
  upgrade_install  = true

  depends_on = [
    helm_release.cert-manager
  ]
}

resource "kubectl_manifest" "knative-serving" {
  yaml_body = <<YAML
apiVersion: operator.knative.dev/v1beta1
kind: KnativeServing
metadata:
  name: knative-serving
  namespace: knative-serving
spec:
  version: "${var.knative_serving_version}"
YAML

  depends_on = [
    helm_release.knative-operator
  ]
}

resource "helm_release" "kserve-crd" {
  name             = "kserve-crd"
  chart            = "kserve-crd"
  namespace        = "kserve"
  version          = var.kserve_version
  repository       = "oci://ghcr.io/kserve/charts"
  create_namespace = true
  upgrade_install  = true

  depends_on = [
    kubectl_manifest.knative-serving
  ]
}

resource "helm_release" "kserve" {
  name            = "kserve"
  chart           = "kserve"
  namespace       = "kserve"
  version         = var.kserve_version
  repository      = "oci://ghcr.io/kserve/charts"
  upgrade_install = true

  set {
    name  = "kserve.modelmesh.enabled"
    value = "false"
  }

  depends_on = [
    helm_release.kserve-crd
  ]
}
