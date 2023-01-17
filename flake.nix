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
      argoGenerate = {
        type = "app";
        program = "${writeShellScript "argo-generate" ''
          cd k8s
          ${jsonnet-bundler}/bin/jb install
          ${sops}/bin/sops -d ./environments/default/secrets.sops.yaml | \
            ${tanka}/bin/tk show --dangerous-allow-redirect environments/default \
            --tla-code "secrets_yaml=importstr '/dev/stdin'"
        ''}";
      };
    });
  };
}
