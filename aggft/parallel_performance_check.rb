#!/usr/bin/env ruby

require "optimist"

opts = Optimist::options do
  opt :runs,      "Number of runs in total",     :type => :int, :required => true
  opt :processes, "Processes to split the work", :type => :int, :required => true
end

RUNS      = opts[:runs]
PROCESSES = opts[:processes]

runs_per_process = (RUNS / PROCESSES).to_i
tmp_dir          = `mktemp --directory`.strip

STDERR.puts "RUNS            : #{RUNS}"
STDERR.puts "PROCESSES       : #{PROCESSES}"
STDERR.puts "RUNS PER PROCESS: #{runs_per_process}"
STDERR.puts "TMP DIR         : #{tmp_dir}"

# Print CSV header
HEADER = [
  "SM COUNT",
  "N MIN CONSTANT",
  "N MIN",
  "PRIVACY TYPE",
  "P",
  "Terminated",
  "Success",
  "TOTAL DC TIME",
  "PHASE 1 DC TIME",
  "MAX TOTAL SM TIME",
  "MIN TOTAL SM TIME",
  "AVG TOTAL SM TIME",
  "STD TOTAL SM TIME",
  "PHASE 1 COUNT",
  "PHASE 2 COUNT",
  "DC NET SND COUNT",
  "DC NET SND SIZE",
  "DC NET RCV COUNT",
  "DC NET RCV SIZE",
  "MAX SM NET SND COUNT",
  "MAX SM NET SND SIZE",
  "MAX SM NET RCV COUNT",
  "MAX SM NET RCV SIZE",
  "MIN SM NET SND COUNT",
  "MIN SM NET SND SIZE",
  "MIN SM NET RCV COUNT",
  "MIN SM NET RCV SIZE",
  "AVG SM NET SND COUNT",
  "AVG SM NET SND SIZE",
  "AVG SM NET RCV COUNT",
  "AVG SM NET RCV SIZE",
  "STD SM NET SND COUNT",
  "STD SM NET SND SIZE",
  "STD SM NET RCV COUNT",
  "STD SM NET RCV SIZE"
].join ","
STDOUT.puts HEADER

PROCESSES.times do |i|
  j = "#{i + 1}".rjust("#{PROCESSES}".length, "0") # Padded for display
  pid = Process.fork do
    cmd = "./aggft/performance_check.py #{runs_per_process}"
    `#{cmd} 1> #{tmp_dir}/#{j}.out 2> #{tmp_dir}/#{j}.err`
  end
end

Process.waitall

STDOUT.puts `cat #{tmp_dir}/*.out`
STDERR.puts `cat #{tmp_dir}/*.err`

`rm -rf #{tmp_dir}`
