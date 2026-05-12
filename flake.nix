{
  description = "startaste — own your stars, upvotes, and favorites";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";

  inputs.pyproject-nix.url = "github:pyproject-nix/pyproject.nix";

  outputs =
    { nixpkgs, pyproject-nix, ... }:
    let
      # Load/parse requirements.txt
      project = pyproject-nix.lib.project.loadRequirementsTxt { projectRoot = ./.; };

      pkgs = nixpkgs.legacyPackages.x86_64-linux;
      python = pkgs.python3;

      pythonEnv =
          pkgs.python3.withPackages (project.renderers.withPackages { inherit python; });

      startaste = python.pkgs.buildPythonApplication {
        pname = "startaste";
        version = builtins.replaceStrings [ "\n" ] [ "" ] (builtins.readFile ./VERSION);
        src = ./.;
        format = "pyproject";
        build-system = [ python.pkgs.setuptools ];
        dependencies = with python.pkgs; [
          requests
          beautifulsoup4
          peewee
          python-dotenv
        ];
      };

    in
    {
      packages.x86_64-linux.default = startaste;
      devShells.x86_64-linux.default = pkgs.mkShell { packages = [ pythonEnv ]; };
    };
}
