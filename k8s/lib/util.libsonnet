local k = import 'github.com/grafana/jsonnet-libs/ksonnet-util/kausal.libsonnet';
local ingress = k.networking.v1.ingress;
local ingressTLS = k.networking.v1.ingressTLS;
local ingressRule = k.networking.v1.ingressRule;
local httpIngressPath = k.networking.v1.httpIngressPath;
{
  ingressFor(service, domain, portName)::
    local name = service.metadata.name;
    ingress.new(name)
    + ingress.metadata.withAnnotations({
      'kubernetes.io/ingress.class': 'nginx',
      'cert-manager.io/cluster-issuer': 'letsencrypt-prod',
    })
    + ingress.spec.withTls(
      ingressTLS.withHosts(domain)
      + ingressTLS.withSecretName('%s-tls' % name)
    )
    + ingress.spec.withRules(
      ingressRule.withHost(domain)
      + ingressRule.http.withPaths(
        httpIngressPath.withPath('/')
        + httpIngressPath.withPathType('Prefix')
        + httpIngressPath.backend.service.withName(name)
        + httpIngressPath.backend.service.port.withName(portName)
      )
    ),

  withSecrets(obj)::
    function(secrets_yaml) {
      _config+:: {
        secrets+: std.native('parseYaml')(secrets_yaml)[0],
      },
    } + obj,
}
