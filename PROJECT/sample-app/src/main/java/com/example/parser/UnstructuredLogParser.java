package com.example.parser;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Parser for unstructured log files. This class demonstrates how to process
 * irregular text input using regular expressions and concurrency. Each log
 * line may or may not contain all parts (timestamp, level, key/value pairs).
 */
public class UnstructuredLogParser {
    private static final Pattern LOG_PATTERN = Pattern.compile(
            "^(?<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})?\s*"
            + "(?<level>[A-Z]+)?\s*"
            + "(?<kv>(?:\w+=\S+\s*)*)"
            + "(?<message>.*)$");

    private final DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

    /**
     * Parse the given log file concurrently. Each line is processed by
     * a separate task to demonstrate parallel parsing. Lines that do not
     * match the expected pattern will result in a {@link LogRecord} with
     * null fields except for the raw message.
     *
     * @param path path to the log file
     * @return list of parsed log records
     * @throws IOException if an I/O error occurs reading from the file
     */
    public List<LogRecord> parseLogs(Path path) throws IOException {
        List<String> lines = Files.readAllLines(path);
        ExecutorService executor = Executors.newFixedThreadPool(Runtime.getRuntime().availableProcessors());
        List<Future<LogRecord>> futures = new ArrayList<>();
        for (String line : lines) {
            futures.add(executor.submit(() -> parseLine(line)));
        }
        List<LogRecord> records = new ArrayList<>();
        for (Future<LogRecord> f : futures) {
            try {
                records.add(f.get());
            } catch (InterruptedException | ExecutionException e) {
                // Wrap exceptions in a LogRecord to avoid stopping other tasks
                LogRecord errorRecord = new LogRecord();
                errorRecord.setMessage("Error parsing line: " + e.getMessage());
                records.add(errorRecord);
            }
        }
        executor.shutdown();
        return records;
    }

    private LogRecord parseLine(String line) {
        Matcher m = LOG_PATTERN.matcher(line);
        LogRecord record = new LogRecord();
        if (m.matches()) {
            String ts = m.group("timestamp");
            String level = m.group("level");
            String kv = m.group("kv").trim();
            String msg = m.group("message").trim();
            if (ts != null && !ts.isEmpty()) {
                record.setTimestamp(LocalDateTime.parse(ts, formatter));
            }
            record.setLevel(level);
            record.setMessage(msg);
            record.setKeyValuePairs(kv);
        } else {
            record.setMessage(line);
        }
        return record;
    }

    /**
     * Immutable log record used to hold the results of parsing. For brevity,
     * the setter methods are not thread safe, but in practice you may wish
     * to use a builder or record type.
     */
    public static class LogRecord {
        private LocalDateTime timestamp;
        private String level;
        private String keyValuePairs;
        private String message;

        public LocalDateTime getTimestamp() {
            return timestamp;
        }
        public void setTimestamp(LocalDateTime timestamp) {
            this.timestamp = timestamp;
        }
        public String getLevel() {
            return level;
        }
        public void setLevel(String level) {
            this.level = level;
        }
        public String getKeyValuePairs() {
            return keyValuePairs;
        }
        public void setKeyValuePairs(String keyValuePairs) {
            this.keyValuePairs = keyValuePairs;
        }
        public String getMessage() {
            return message;
        }
        public void setMessage(String message) {
            this.message = message;
        }
    }
}