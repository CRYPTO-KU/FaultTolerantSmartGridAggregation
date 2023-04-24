{
  description = "AggFT Algorithm Implementation";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = {
    self,
    nixpkgs,
    flake-utils,
  }:
    flake-utils.lib.eachDefaultSystem (system: let
      pkgs = import nixpkgs {inherit system;};

      ourPython = pkgs.python310;

      pythonEnv = ourPython.withPackages (pythonPkgs:
        with pythonPkgs; [
          aiohttp
          phe
          pyaes
          rich
        ]);

      format-code = with pkgs;
        writeShellScriptBin "format-code" ''
          ${ourPython.pkgs.isort}/bin/isort aggft
          ${autoflake}/bin/autoflake -r --in-place --remove-unused-variables aggft
          ${black}/bin/black aggft
        '';
    in {
      devShell = pkgs.mkShell {
        nativeBuildInputs = with pkgs; [
          pythonEnv
          ruby
          format-code
        ];
        buildInputs = [];
      };
    });
}
