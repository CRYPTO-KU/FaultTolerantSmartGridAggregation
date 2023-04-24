#!/usr/bin/env ruby

RUNS      = ARGV[0].to_i
PROCESSES = ARGV[1].to_i

runs_per_process = (RUNS / PROCESSES).to_i

# Print CSV header
puts "SM COUNT,PRIVACY TYPE,P,Terminated,Success,TOTAL DC TIME,PHASE 1 DC TIME,MAX TOTAL SM TIME,PHASE 1 COUNT,PHASE 2 COUNT,DC NET SND,DC NET RCV,MAX SM NET SND,MAX SM NET RCV"

# Spawn processes
PROCESSES.times { spawn "./aggft/performance_check.py #{runs_per_process}" }

# Wait for all of them to finish
Process.waitall
