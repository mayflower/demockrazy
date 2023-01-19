{ uwsgi, dockerTools }:

dockerTools.buildImage {
  name = "demockrazy-uwsgi";
  tag = "latest";
  copyToRoot = [ uwsgi ];
  config = {
    Entrypoint = [
      "demockrazy-uwsgi"
    ];
    ExposedPorts."3000/tcp" = {};
  };
}
