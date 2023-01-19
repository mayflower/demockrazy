{
  description = "A simple token based voting system";

  inputs = {
    nixpkgs.url = "github:mayflower/nixpkgs/mf-stable";
    argocd-nix-flakes-plugin = {
      url = "github:mayflower/argocd-nix-flakes-plugin";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, argocd-nix-flakes-plugin }: let
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
          python3Packages.psycopg2
          tanka
          jsonnet-bundler
          sops
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
        # FIXME is this really a nice solution? Check if this can cause small downtimes.
        pushd ${self} &>/dev/null
          ${lib.concatMapStrings (cmd: ''
            DJANGO_SETTINGS_MODULE=demockrazy_config ${djangoEnv.${system}}/bin/python3 manage.py ${cmd}
          '') [ "makemigrations" "migrate" ]}
        popd &>/dev/null
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
      default = callPackage ./nix/demockracy-image.nix {
        uwsgi = self.packages.${system}.uwsgi;
      };
      nginx = callPackage ./nix/nginx-image.nix { };
    });
    apps = forEachSystem (system: with pkgs.${system}; {
      inherit (argocd-nix-flakes-plugin.apps.${system}) tankaShow tankaEval;
    });
  };
}
