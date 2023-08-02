{
  buildPythonApplication,
  aggft-core,
}:
buildPythonApplication {
  pname = "aggft-simulate";
  version = "0.1.0";

  src = ../../src/simulate;
  doCheck = false;

  propagatedBuildInputs = [aggft-core];
}
