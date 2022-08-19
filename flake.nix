{
	description = "YouTube Music Downloader";

	inputs = {
		nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
		flake-utils.url = "github:numtide/flake-utils";
	};

	outputs = { self, nixpkgs, flake-utils }:
	flake-utils.lib.eachDefaultSystem (system: let
		pkgs = import nixpkgs { inherit system; };

		python = pkgs.python3;
		pythonPkgs = python.pkgs;
		buildPythonApplication = pythonPkgs.buildPythonApplication;

		dependencies = rec {
			python = with pythonPkgs; {
				build = [ flit ];
				test = [ pytest pytest-asyncio ];
				runtime = [ aiohttp phe sortedcontainers ];
			};
			other = with pkgs; {
				build = [ ];
				test = [ ];
				runtime = [ ];
			};
			build = other.build python.build;
			test = other.test python.test;
			runtime = other.runtime python.runtime;
		};

		pythonDevelopmentEnvironment = python.withPackages (_:
			dependencies.python.build ++
			dependencies.python.test ++
			dependencies.python.runtime
		);
	in {
		devShell = pkgs.mkShell {
			nativeBuildInputs = with pkgs;
				[ pythonDevelopmentEnvironment ] ++
				dependencies.other.build ++
				dependencies.other.test ++
				dependencies.other.runtime
			;
			buildInputs = [ ];
		};
	});
}
