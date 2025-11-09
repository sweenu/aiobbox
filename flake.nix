{
  description = "Async Python API wrapper for Bouygues Telecom routers";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        python = pkgs.python313;
        pythonPackages = python.pkgs;
      in
      {
        devShells.default = pkgs.mkShell {
          packages = with pkgs; [
            python
            uv
          ];
        };

        packages.default = pythonPackages.buildPythonPackage {
          pname = "aiobbox";
          version = "0.3.0";
          src = ./.;
          pyproject = true;

          propagatedBuildInputs = with pythonPackages; [
            aiohttp
            pydantic
          ];

          nativeBuildInputs = with pythonPackages; [
            uv-build
          ];

          pythonImportsCheck = [ "aiobbox" ];

          meta = with pkgs.lib; {
            description = "Async Python API wrapper for Bouygues Telecom routers";
            homepage = "https://github.com/sweenu/aiobbox";
            license = licenses.asl20;
          };
        };
      }
    );
}
