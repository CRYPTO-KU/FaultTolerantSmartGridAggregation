# Development environment
# You can enter it through `nix develop` or (legacy) `nix-shell`
{pkgs ? (import ./nixpkgs.nix) {}}: {
  default = pkgs.mkShell {
    nativeBuildInputs = with pkgs; [
      # Command runner
      just

      # Python Environment
      (python310.withPackages (ps:
        with ps; [
          aiohttp
          phe
          pyaes

          # custom package
          aggft-core
        ]))

      # Python Formatter
      black

      # custom package
      aggft-simulate

      # Ruby Environment
      (ruby.withPackages (ps:
        with ps; [
          optimist
        ]))

      # Ruby Formatter
      rufo
    ];
  };
}
