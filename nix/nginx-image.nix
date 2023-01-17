{ dockerTools, writeText, nginx, fakeNss, mailcap }:

dockerTools.buildLayeredImage {
  name = "demockrazy-reverse-proxy";
  tag = "latest";
  contents = [ nginx fakeNss ];
  extraCommands = "mkdir -p var/cache/nginx/client_body";
  config = {
    Entrypoint = [
      "nginx"
      "-c"
      (writeText "nginx.conf" ''
        user nobody nobody;
        daemon off;
        error_log /dev/stdout info;
        pid /dev/null;
        events {}
        http {
          access_log /dev/stdout;
          include ${nginx}/conf/uwsgi_params;
          server {
            listen 80;
            location / {
              uwsgi_pass 127.0.0.1:3000;
            }
            location /static/ {
              include ${mailcap}/etc/nginx/mime.types;
              alias ${../vote/static}/;
            }
          }
        }
      '')
    ];
    ExposedPorts."80/tcp" = {};
  };
}
