local k = import 'github.com/grafana/jsonnet-libs/ksonnet-util/kausal.libsonnet';
local util = import 'util.libsonnet';
local deployment = k.apps.v1.deployment;
local container = k.core.v1.container;
local port = k.core.v1.containerPort;
local envVar = k.core.v1.envVar;

function (secrets_yaml, commit_hash) util.withSecrets ({
  _config+:: {
    local config = self,
    domain: 'briefwahl.mayflower.cloud',
    tag: commit_hash,
    images: {
      default: 'ghcr.io/mayflower/demockrazy/default:%s' % config.tag,
      nginx: 'ghcr.io/mayflower/demockrazy/nginx:%s' % config.tag,
    },
    database: {
      name: 'demockrazy',
      cluster: 'demockrazy-cluster'
    },
  },
  serviceSecrets: k.core.v1.secret.new(
    'demockrazy-service-secrets',
    {
      'email_from': std.base64($._config.secrets.email_from),
      'email_host': std.base64($._config.secrets.email_host),
      'email_password': std.base64($._config.secrets.email_password),
      'secret_key': std.base64($._config.secrets.secret_key),
    }
  ),
  service: {
    local cfg = $._config,
    local upstreamPort = 'web',
    deployment: deployment.new(
      name='demockrazy',
      replicas=1,
      containers=[
        container.new('backend-nginx', cfg.images.nginx)
        + container.withPorts([port.new(upstreamPort, 80)]),
        container.new('backend-uwsgi', cfg.images.default)
        + container.withEnvMap({
          DEMOCKRAZY_DB_NAME: cfg.database.name,
          DEMOCKRAZY_DB_HOST: cfg.database.cluster,
          DEMOCKRAZY_DOMAIN: cfg.domain,
        })
        + container.withEnvMixin([
          envVar.fromSecretRef(
            'DEMOCKRAZY_DB_USER',
            '%s-owner-user.%s.credentials.postgresql.acid.zalan.do'
            % [cfg.database.name, cfg.database.cluster],
            'username'
          ),
          envVar.fromSecretRef(
            'DEMOCKRAZY_DB_PW',
            '%s-owner-user.%s.credentials.postgresql.acid.zalan.do'
            % [cfg.database.name, cfg.database.cluster],
            'password'
          ),
          envVar.fromSecretRef(
            'DEMOCKRAZY_SECRET_KEY',
            'demockrazy-service-secrets',
            'secret_key'
          ),
          envVar.fromSecretRef(
            'DEMOCKRAZY_EMAIL_HOST',
            'demockrazy-service-secrets',
            'email_host'
          ),
          envVar.fromSecretRef(
            'DEMOCKRAZY_EMAIL_PASSWORD',
            'demockrazy-service-secrets',
            'email_password'
          ),
          envVar.fromSecretRef(
            'DEMOCKRAZY_VOTE_MAIL_FROM',
            'demockrazy-service-secrets',
            'email_from'
          ),
        ])
      ]
    ),
    service: k.util.serviceFor(self.deployment, nameFormat="%(port)s"),
    ingress: util.ingressFor(self.service, cfg.domain, upstreamPort),
  },
  database: {
    local cfg = $._config,
    apiVersion: 'acid.zalan.do/v1',
    kind: 'postgresql',
    metadata: { name: cfg.database.cluster },
    spec: {
      teamId: 'demockrazy',
      volume: { size: '1Gi' },
      numberOfInstances: 1,
      users: { root: [ 'superuser', 'createdb' ] },
      preparedDatabases: { [cfg.database.name]: { defaultUsers: true } },
      postgresql: { version: '14' },
    }
  }
})(secrets_yaml)
