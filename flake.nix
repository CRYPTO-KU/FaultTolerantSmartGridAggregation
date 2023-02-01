{
	description = "AggFT Algorithm Implementation";

	inputs = {
		nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
		flake-utils.url = "github:numtide/flake-utils";
	};

	outputs = { self, nixpkgs, flake-utils }:
	flake-utils.lib.eachDefaultSystem (system: let
		pkgs = import nixpkgs { inherit system; };

		pythonEnv = pkgs.python3.withPackages (pythonPkgs: with pythonPkgs; [
			aiohttp
			phe
			pyaes
			rich 
		]);
	in {
		devShell = pkgs.mkShell {
			nativeBuildInputs = [ pythonEnv ];
			buildInputs = [ ];
		};
	});
}
