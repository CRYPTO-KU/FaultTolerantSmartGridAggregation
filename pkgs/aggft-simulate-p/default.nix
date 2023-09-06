{
  writeShellScriptBin,
  jq,
  moreutils,
  aggft-simulate,
}:
writeShellScriptBin "aggft-sim-p" ''
  ${aggft-simulate}/bin/aggft-headers

  PROCS=$(cat $1 | ${jq}/bin/jq ".processes")
  ARGS=$(for i in `seq $PROCS`; do echo -n "$1 "; done)
  ${moreutils}/bin/parallel ${aggft-simulate}/bin/aggft-sim -- $ARGS
''
