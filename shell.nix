# Development environment
# You can enter it through `nix develop` or (legacy) `nix-shell`
{pkgs ? (import ./nixpkgs.nix) {}}: {
  default = pkgs.mkShell {
    nativeBuildInputs = with pkgs; [
      # Command runner
      just

      # compression programs
      p7zip

      # Python Formatter
      black

      # Python Environment
      (python310.withPackages (ps:
        with ps; [
          aiohttp
          phe
          pyaes

          # custom package
          aggft-core
        ]))

      # custom packages
      aggft-simulate
      aggft-simulate-p
      aggft-simulate-fig-p
    ];
  };
}
