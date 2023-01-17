{
  description = "A simple token based voting system";

  inputs.nixpkgs.url = "github:mayflower/nixpkgs/mf-stable";

  outputs = { self, nixpkgs }: let
    inherit (nixpkgs) lib;
    forEachSystem = lib.genAttrs [ "x86_64-linux" ];
    pkgs = forEachSystem (system: nixpkgs.legacyPackages.${system});
    uwsgi = forEachSystem (system: pkgs.${system}.uwsgi.override { plugins = [ "python3" ]; });
    djangoEnv = forEachSystem (system: uwsgi.${system}.python3.withPackages (ps: [
      ps.django
      ps.psycopg2
      self.packages.${system}.django_config
    ]));
  in {
    devShells = forEachSystem (system: with pkgs.${system}; {
      default = mkShell {
        name = "demockrazy-env";
        buildInputs = [
          python3
          python3Packages.django
        ];
      };
    });
    packages = forEachSystem (system: with pkgs.${system}; {
      django_config = uwsgi.${system}.python3.pkgs.buildPythonPackage {
        name = "demockrazy-config";
        format = "other";
        dontUnpack = true;
        installPhase = ''
          install -D \
            ${self}/k8s/settings.py \
            $out/${uwsgi.${system}.python3.sitePackages}/demockrazy_config/__init__.py
        '';
      };
      uwsgi = writeShellScriptBin "demockrazy-uwsgi" ''
        ${uwsgi.${system}}/bin/uwsgi \
          --json ${writeText "demockrazy.json" (builtins.toJSON {
            uwsgi = {
              buffer-size = 8192;
              chdir = self;
              env = "DJANGO_SETTINGS_MODULE=demockrazy_config";
              master = self;
              plugins = [ "python3" ];
              protocol = "uwsgi";
              pythonpath = "${djangoEnv.${system}}/${uwsgi.${system}.python3.sitePackages}";
              wsgi-file = "demockrazy/wsgi.py";
              socket = "0.0.0.0:3000";
            };
          })}
      '';
    });
    dockerImages = forEachSystem (system: with pkgs.${system}; {
      default = dockerTools.buildImage {
        name = "demockrazy-uwsgi";
        tag = "latest";
        copyToRoot = [ self.packages.${system}.uwsgi ];
        config = {
          Entrypoint = [
            "demockrazy-uwsgi"
          ];
          ExposedPorts."3000/tcp" = {};
        };
      };
      nginx = dockerTools.buildLayeredImage {
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
                    alias ${./vote/static}/;
                  }
                }
              }
            '')
          ];
          ExposedPorts."80/tcp" = {};
        };
      };
    });
  };
}
