package com.example.integrated;

import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;

public class IntegratedService {

    public void startProcess() {
        doWork();
    }

    private int doWork() {
        List<BigDecimal> items = new ArrayList<>();
        items.add(new BigDecimal("10.50"));
        items.add(new BigDecimal("20.00"));
        BigDecimal total = calculateOrderTotal(items);
        String id = getFormattedId("123");
        String userData = getStaticUserData(id);
        log("Processed: " + userData + ", total=" + total);
        return total.intValue();
    }

    public static String getStaticUserData(String id) {
        return "USR-" + id;
    }

    public BigDecimal calculateOrderTotal(List<BigDecimal> items) {
        BigDecimal total = BigDecimal.ZERO;
        for (BigDecimal b : items) {
            total = total.add(b);
        }
        return total;
    }

    String getFormattedId(String id) {
        return String.format("%s-%s", "ID", id);
    }

    private void log(String msg) {
        System.out.println(msg);
    }
}

