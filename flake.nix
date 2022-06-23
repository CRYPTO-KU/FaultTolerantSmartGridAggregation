{
	description = "Proven Smart Grid Security Implementation";

	inputs = {
		nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
		flake-utils.url = "github:numtide/flake-utils";
		mach-nix.url = "github:DavHau/mach-nix/3.5.0";
	};

	outputs = { self, nixpkgs, mach-nix, flake-utils }:
	flake-utils.lib.eachDefaultSystem (system: let
		python = "python39";

		pkgs = import nixpkgs { inherit system; };
		mach = import mach-nix { inherit pkgs python; };

		python-env = (mach.mkPython {
			requirements = builtins.readFile ./requirements.txt;
			packagesExtra = [];
			ignoreCollisions = false;
		});
	in {
		devShell = pkgs.mkShell {
			nativeBuildInputs = with pkgs; [
				python-env
			];
			buildInputs = [ ];
		};
	});
}
