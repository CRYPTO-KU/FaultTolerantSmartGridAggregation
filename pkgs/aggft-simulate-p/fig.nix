{
  writeShellScriptBin,
  jq,
  parallel,
  aggft-simulate,
}:
writeShellScriptBin "aggft-sim-fig-p" ''
  ${aggft-simulate}/bin/aggft-headers

  PROCS=$(cat $1 | ${jq}/bin/jq ".processes")
  yes $1 | head -n $PROCS | ${parallel}/bin/parallel ${aggft-simulate}/bin/aggft-sim-fig {}
''
