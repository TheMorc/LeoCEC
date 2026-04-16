{
  description = "LeoCEC TV control service";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs = { self, nixpkgs }:
  let
    system = "x86_64-linux";
    pkgs = import nixpkgs { inherit system; };

    python = pkgs.python3;
  in
  {
    packages.${system}.default =
      python.pkgs.buildPythonApplication {
        pname = "leocec";
        version = "0.1.0";
        src = ./.;

pyproject = true;

  build-system = [ pkgs.python3Packages.setuptools ];


        propagatedBuildInputs = [
          python.pkgs.dbus-next
	python.pkgs.pyserial
        ];
      };

nixosModules.default = { config, lib, pkgs, ... }:
    let
      cfg = config.services.leocec;
    in
    {
      options.services.leocec = {
        enable = lib.mkEnableOption "LeoCEC TV control service";
	serialPort = lib.mkOption {
		type = lib.types.str;
		default = "/dev/serial/by-id/usb-Arduino_LLC_Arduino_Leonardo-if00";
		description = "Serial port path for the LeoCEC flashed Arduino";
	};

      };

      config = lib.mkIf cfg.enable {
        systemd.user.services.leocec = {
  description = "LeoCEC TV control service";
  wantedBy = [ "multi-user.target" ];
  after = [ "network.target" ];

  serviceConfig = {
    ExecStart = "${self.packages.${pkgs.system}.default}/bin/leocec";
    Restart = "always";
    Environment = [
      "PYTHONUNBUFFERED=1"
      "LEOCEC_PORT=${cfg.serialPort}"
    ];
  };
        };
      };
    };

    apps.${system}.default = {
      type = "app";
      program = "${self.packages.${system}.default}/bin/leocec";
    };
  };
}
