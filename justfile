reload-nix-shell:
  cd {{justfile_directory()}}
  touch shell.nix

format-code:
  cd {{justfile_directory()}}
  nix fmt
  black .
