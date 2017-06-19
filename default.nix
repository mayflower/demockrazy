with import <nixpkgs> {}; {
  env = stdenv.mkDerivation {
    name = "demockrazy-env";
    buildInputs = [
      python3
      python3Packages.django_1_11
    ];
  };
}
