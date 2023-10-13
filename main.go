package main

import (
	"bufio"
	"encoding/json"
	"flag"
	"fmt"
	"log"
	"os"
	"path/filepath"
	"reflect"
	"slices"
	"strconv"
	"strings"

	"github.com/adrg/strutil"
	"github.com/adrg/strutil/metrics"
)

func check(e error) {
	if e != nil {
		log.Panic(e)
	}
}

func getEntries(fname string) []map[string]interface{} {
	logFile, err := os.Open(fname)
	check(err)
	defer logFile.Close()

	var entries []map[string]interface{}

	scanner := bufio.NewScanner(logFile)
	for scanner.Scan() {
		var entry = parseJson(scanner.Text())
		entries = append(entries, entry)

	}

	if err := scanner.Err(); err != nil {
		log.Panic(err)
	}

	return entries
}

func parseJson(entry string) map[string]interface{} {
	var result map[string]interface{}
	json.Unmarshal([]byte(entry), &result)

	return result
}

func removeSlices(entries []map[string]interface{}) []map[string]interface{} {
	var new_entries []map[string]interface{}

	for _, e := range entries {
		message := e["message"]
		if message == nil {
			continue
		}

		if reflect.ValueOf(message).Kind() != reflect.Slice {
			new_entries = append(new_entries, e)
		}
	}

	return new_entries
}

func getSessions(entries []map[string]interface{}) []string {
	var sessions []string
	for _, e := range entries {
		if e["eventid"] == "cowrie.login.success" {
			sessions = append(sessions, e["session"].(string))
		}

	}

	return sessions
}

func getAllCommands(entries []map[string]interface{}, sessions []string) []string {
	var allCommands []string
	for _, s := range sessions {
		commands := ""
		for _, e := range entries {
			if e["session"] == s {
				if strings.Contains(e["message"].(string), "CMD") {
					message := strings.Replace(e["message"].(string), "CMD: ", "", 1)
					commands += message + "\n"
				}
			}
		}

		if commands == "" {
			continue
		}

		allCommands = append(allCommands, commands)
	}

	return allCommands
}

func getUniqueCommands(allCommands []string, ratio float64) []string {
	var uniqueCommands []string
	uniqueCommands = append(uniqueCommands, "0")
	for _, ac := range allCommands {
		var ratios []float64
		for _, uc := range uniqueCommands {
			similarity := strutil.Similarity(uc, ac, metrics.NewLevenshtein())
			ratios = append(ratios, similarity)
		}

		if slices.Max(ratios) > ratio {
			continue
		}

		uniqueCommands = append(uniqueCommands, ac)
	}

	return uniqueCommands
}

func main() {

	var fname string
	flag.StringVar(&fname, "f", "", "Specify cowrie json log file")

	var output string
	flag.StringVar(&output, "o", "", "Specify output location for report (default ./report_[filename])")

	var ratio string
	flag.StringVar(&ratio, "r", "0.7", "Specify similarity ratio as a float")

	flag.Parse()

	if fname == "" {
		fmt.Println("Please specify -f. Use --help for more information.")
		os.Exit(2)
	}

	if output == "" {
		output = "./report_" + filepath.Base(fname)
	}

	r, err := strconv.ParseFloat(ratio, 8)
	check(err)

	entries := removeSlices(getEntries(fname))
	sessions := getSessions(entries)
	allCommands := getAllCommands(entries, sessions)
	uniqueCommands := getUniqueCommands(allCommands, r)

	f, err := os.Create(output)
	check(err)
	defer f.Close()

	for _, c := range uniqueCommands[1:] {
		f.WriteString(strings.Repeat("-", 50) + "\n")
		_, err = f.WriteString(strings.TrimSuffix(c, "\n") + "\n")
		check(err)
		f.WriteString(strings.Repeat("-", 50) + "\n\n")
	}
}
