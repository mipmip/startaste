{
  description = "startaste — own your stars, upvotes, and favorites";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";

  inputs.pyproject-nix.url = "github:pyproject-nix/pyproject.nix";

  outputs =
    { self, nixpkgs, pyproject-nix, ... }:
    let
      # Supported systems, enumerated explicitly (plain nix, no flake-utils).
      systems = [ "x86_64-linux" "aarch64-linux" ];

      forAllSystems = f: nixpkgs.lib.genAttrs systems f;

      # Load/parse requirements.txt (dev shell only; the package pins its own deps).
      project = pyproject-nix.lib.project.loadRequirementsTxt { projectRoot = ./.; };

      version = builtins.replaceStrings [ "\n" ] [ "" ] (builtins.readFile ./VERSION);

      startasteFor = pkgs:
        let
          python = pkgs.python3;
        in
        python.pkgs.buildPythonApplication {
          pname = "startaste";
          inherit version;
          src = ./.;
          format = "pyproject";
          build-system = [ python.pkgs.setuptools ];
          dependencies = with python.pkgs; [
            requests
            beautifulsoup4
            peewee
            python-dotenv
            flask
          ];
        };

      nixpkgsFor = forAllSystems (system: import nixpkgs {
        inherit system;
        overlays = [ self.overlays.default ];
      });

    in
    {
      overlays.default = final: _prev: {
        startaste = startasteFor final;
      };

      packages = forAllSystems (system: {
        default = nixpkgsFor.${system}.startaste;
        startaste = nixpkgsFor.${system}.startaste;
      });

      devShells = forAllSystems (system:
        let
          pkgs = nixpkgsFor.${system};
          pythonEnv = pkgs.python3.withPackages
            (project.renderers.withPackages { python = pkgs.python3; });
        in
        {
          default = pkgs.mkShell { packages = [ pythonEnv ]; };
        });

      nixosModules.startaste = import ./nix/module.nix;

      # Only the NixOS module test. A build/test/coverage gate is separate
      # release tooling and is not wired up here.
      checks = forAllSystems (system: {
        nixos-module = nixpkgsFor.${system}.testers.runNixOSTest
          (import ./nix/tests/module.nix { inherit self; });
      });

      formatter = forAllSystems (system: nixpkgsFor.${system}.nixpkgs-fmt);
    };
}
