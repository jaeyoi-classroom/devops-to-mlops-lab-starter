resource "helm_release" "monitoring_stack" {
  name       = "prometheus"
  chart      = "kube-prometheus-stack"
  repository = "https://prometheus-community.github.io/helm-charts"
  namespace  = "monitoring"
  version    = "63.1.0"
  create_namespace = true

  values = [
    "${file("prometheus-values.yml")}"
  ]
}