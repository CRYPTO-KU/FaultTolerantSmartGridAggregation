{
  buildPythonPackage,
  aiohttp,
  phe,
  pyaes,
}:
buildPythonPackage {
  pname = "aggft-core";
  version = "0.1.0";

  src = ../../src/core;
  doCheck = false;

  propagatedBuildInputs = [aiohttp phe pyaes];
}
