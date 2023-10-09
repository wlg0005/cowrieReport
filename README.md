# cowrieReport
CLI tool to parse cowrie json logs and generate a report of commands ran by attackers

Current usage is primarily focused on using an 'exclude' file containing regular expressions to reduce the noise generated by certain bots. In testing, this has reduced the report file from 16k lines to under 350 lines making it much easier to find interesting behavior on the honeypot.

## Usage
```
Usage: cli.py [OPTIONS]

  Remove noisy sets of commands in a cowrie json log using regular expressions

Options:
  -d, --dir TEXT      Specify directory containing cowrie json logs NOTE: This
                      argument is mutually exclusive with log
  -l, --log TEXT      Specify a cowrie json log file NOTE: This argument is
                      mutually exclusive with dir
  -e, --exclude TEXT  Specify an exclusions file (regular expressions on each
                      line)  [required]
  -o, --output TEXT   Specify output directory to store report
  --help              Show this message and exit.
```
