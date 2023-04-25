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
STDOUT.puts "SM COUNT,PRIVACY TYPE,P,Terminated,Success,TOTAL DC TIME,PHASE 1 DC TIME,MAX TOTAL SM TIME,PHASE 1 COUNT,PHASE 2 COUNT,DC NET SND,DC NET RCV,MAX SM NET SND,MAX SM NET RCV"

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
