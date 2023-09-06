{
  writeShellScriptBin,
  jq,
  parallel,
  aggft-simulate,
}:
writeShellScriptBin "aggft-sim-p" ''
  cleanup() {
      rv=$?
      rm -rf "$TMPDIR"
      exit $rv
  }

  TMPDIR="$(mktemp -d)"
  trap "cleanup" EXIT

  ${aggft-simulate}/bin/aggft-headers

  PROCS=$(cat $1 | ${jq}/bin/jq ".processes")

  yes $1 | head -n $PROCS | PARALLEL_HOME=$TMPDIR ${parallel}/bin/parallel --will-cite ${aggft-simulate}/bin/aggft-sim {}
''
