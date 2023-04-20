puts "PRIVACY TYPE,SM COUNT, FAILURES"
puts `python3 aggft/failure_check.py --privacy-type mask --n 2 --n-min 2`
puts `python3 aggft/failure_check.py --privacy-type encr --n 2 --n-min 2`
puts `python3 aggft/failure_check.py --privacy-type mask --n 3 --n-min 2`
puts `python3 aggft/failure_check.py --privacy-type encr --n 3 --n-min 2`
puts `python3 aggft/failure_check.py --privacy-type mask --n 4 --n-min 2`
puts `python3 aggft/failure_check.py --privacy-type encr --n 4 --n-min 2`
