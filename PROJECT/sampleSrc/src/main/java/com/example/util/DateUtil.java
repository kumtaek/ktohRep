package com.example.util;

import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeParseException;

public class DateUtil {

    private static final String DEFAULT_DATE_FORMAT = "yyyy-MM-dd";

    /**
     * 현재 날짜를 기본 형식 (yyyy-MM-dd)으로 반환합니다.
     * @return 현재 날짜 문자열
     */
    public static String getCurrentDate() {
        return LocalDate.now().format(DateTimeFormatter.ofPattern(DEFAULT_DATE_FORMAT));
    }

    /**
     * 지정된 날짜 문자열을 특정 형식으로 변환합니다.
     * @param dateString 변환할 날짜 문자열
     * @param originalFormat 원본 날짜 형식
     * @param targetFormat 대상 날짜 형식
     * @return 변환된 날짜 문자열, 변환 실패 시 null
     */
    public static String convertDateFormat(String dateString, String originalFormat, String targetFormat) {
        try {
            LocalDate date = LocalDate.parse(dateString, DateTimeFormatter.ofPattern(originalFormat));
            return date.format(DateTimeFormatter.ofPattern(targetFormat));
        } catch (DateTimeParseException e) {
            System.err.println("날짜 형식 변환 실패: " + e.getMessage());
            return null;
        }
    }

    /**
     * 두 날짜 사이의 일수를 계산합니다.
     * @param startDateString 시작 날짜 문자열 (yyyy-MM-dd)
     * @param endDateString 종료 날짜 문자열 (yyyy-MM-dd)
     * @return 두 날짜 사이의 일수, 계산 실패 시 -1
     */
    public static long daysBetween(String startDateString, String endDateString) {
        try {
            LocalDate startDate = LocalDate.parse(startDateString, DateTimeFormatter.ofPattern(DEFAULT_DATE_FORMAT));
            LocalDate endDate = LocalDate.parse(endDateString, DateTimeFormatter.ofPattern(DEFAULT_DATE_FORMAT));
            return java.time.temporal.ChronoUnit.DAYS.between(startDate, endDate);
        } catch (DateTimeParseException e) {
            System.err.println("날짜 차이 계산 실패: " + e.getMessage());
            return -1;
        }
    }
}