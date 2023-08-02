# Custom packages, that can be defined similarly to ones from nixpkgs
# You can build them using `nix build .#example` or (legacy) `nix-build -A example`
{pkgs ? (import ../nixpkgs.nix) {}}: {
  # example = pkgs.callPackage ./example { };

  aggft-simulate = pkgs.callPackage ./aggft-simulate {
    inherit (pkgs.python3.pkgs) buildPythonApplication aggft-core;
  };
}
