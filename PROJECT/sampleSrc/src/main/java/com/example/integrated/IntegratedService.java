package com.example.integrated;

import org.springframework.stereotype.Service;
import org.springframework.beans.factory.annotation.Autowired;
import java.util.List;
import java.util.Map;
import java.util.ArrayList;
import java.util.Optional;

@Service
public class IntegratedService {

    @Autowired
    private IntegratedMapper integratedMapper;

    // --- From Example1: ClassA and ClassB ---
    public void startProcess() {
        doWork();
    }

    private void doWork() {
        System.out.println("Integrated Service: Working...");
    }

    // --- From Example3: Sample.java and Sample_modified.java ---
    /**
     * @MethodName : getStaticUserData
     * @Description : 고정된 SQL 쿼리를 사용하여 사용자 데이터를 조회합니다.
     *                이 메서드는 동적 SQL을 사용하지 않으며, SQL Injection으로부터 안전합니다.
     * @Parameters : 
     * @Return : List<Map<String, Object>> - 사용자 데이터 목록
     */
    public List<Map<String, Object>> getStaticUserData() {
        String sql = "SELECT ID, NAME FROM USERS WHERE STATUS = 'ACTIVE'";
        // In a real application, this would call a mapper or execute directly
        // For analysis, we just need to identify the static SQL string.
        System.out.println("Executing static SQL: " + sql);
        return integratedMapper.executeStaticQuery(sql);
    }

    /**
     * @MethodName : getDynamicUserData
     * @Description : 테이블 이름을 동적으로 구성하여 사용자 데이터를 조회합니다.
     *                이 메서드는 동적 SQL을 사용하므로 SQL Injection에 취약할 수 있습니다.
     * @Parameters : String tableName - 조회할 테이블 이름
     * @Return : List<Map<String, Object>> - 사용자 데이터 목록
     */
    public List<Map<String, Object>> getDynamicUserData(String tableName) {
        String sql = "SELECT ID, NAME FROM " + tableName + " WHERE STATUS = 'ACTIVE'";
        System.out.println("Executing dynamic SQL: " + sql);
        return integratedMapper.executeDynamicQuery(sql);
    }

    /**
     * @MethodName : processWithReflection
     * @Description : 리플렉션을 사용하여 클래스를 로드하는 예제 메서드입니다.
     *                존재하지 않는 클래스를 로드할 경우 예외가 발생하며, 이를 적절히 처리합니다.
     * @Parameters : String className - 로드할 클래스 이름
     * @Return : boolean - 클래스 로드 성공 여부
     */
    public boolean processWithReflection(String className) {
        try {
            Class<?> clazz = Class.forName(className);
            System.out.println("Class loaded successfully: " + clazz.getName());
            return true;
        } catch (ClassNotFoundException e) {
            System.err.println("Class not found: " + className + " - " + e.getMessage());
            // 예외 처리
            return false;
        } catch (Exception e) {
            System.err.println("An unexpected error occurred: " + e.getMessage());
            return false;
        }
    }

    // --- From DynamicMyBatis: DynamicService ---
    public List<Map<String, Object>> getFilteredDynamicData(Map<String, Object> params) {
        return integratedMapper.findDynamicData(params);
    }

    public int updateDynamicStatuses(String status, List<Integer> ids) {
        return integratedMapper.updateDynamicStatus(status, ids);
    }

    // --- From MixedTechLegacy: LegacyService ---
    public List<Map<String, Object>> retrieveLegacyData(String type, String status) {
        Map<String, Object> params = Map.of("dataType", type, "dataStatus", status);
        return integratedMapper.selectLegacyRecords(params);
    }

    public String generateComplexReport(List<Map<String, String>> data) {
        StringBuilder report = new StringBuilder();
        data.forEach(row -> report.append(row.get("REPORT_NAME")).append(" - ").append(row.get("REPORT_VALUE")).append("\n"));
        return report.toString();
    }

    // --- New: Well-commented and poorly commented methods ---
    /**
     * @MethodName : calculateOrderTotal
     * @Description : 주문 항목들의 총 금액을 계산합니다.
     *                각 항목의 수량과 단가를 곱하여 합산합니다.
     * @Parameters : List<Map<String, Object>> orderItems - 주문 항목 목록 (각 Map은 'quantity', 'unitPrice' 키를 포함)
     * @Return : double - 총 주문 금액
     * @Throws : IllegalArgumentException - 주문 항목 목록이 null이거나 비어 있을 경우
     */
    public double calculateOrderTotal(List<Map<String, Object>> orderItems) {
        if (orderItems == null || orderItems.isEmpty()) {
            throw new IllegalArgumentException("Order items cannot be null or empty.");
        }
        double total = 0.0;
        for (Map<String, Object> item : orderItems) {
            int quantity = (Integer) item.get("quantity");
            double unitPrice = (Double) item.get("unitPrice");
            total += quantity * unitPrice;
        }
        return total;
    }

    // Poorly commented method
    public String getFormattedId(String rawId) {
        // Formats ID
        if (rawId == null) return "";
        return rawId.trim().toUpperCase();
    }

    // --- New: Methods calling complex SQL queries ---
    public List<Map<String, Object>> getMonthlySalesAndTopCustomers(String startDate, String endDate) {
        return integratedMapper.getComplexReport(startDate, endDate);
    }

    public List<Map<String, Object>> getProductSalesByRegion(String regionId) {
        return integratedMapper.getProductSalesByRegion(regionId);
    }

    public List<Map<String, Object>> getCustomerOrderSummary(String customerId) {
        return integratedMapper.getCustomerOrderSummary(customerId);
    }

    public List<Map<String, Object>> getEmployeePerformance(String year) {
        return integratedMapper.getEmployeePerformance(year);
    }

    public List<Map<String, Object>> getInventoryStatus(String warehouseId) {
        return integratedMapper.getInventoryStatus(warehouseId);
    }

    // --- New: Large Java file example (simulated with many methods) ---
    public void largeMethod1() { /* ... */ }
    public void largeMethod2() { /* ... */ }
    public void largeMethod3() { /* ... */ }
    public void largeMethod4() { /* ... */ }
    public void largeMethod5() { /* ... */ }
    public void largeMethod6() { /* ... */ }
    public void largeMethod7() { /* ... */ }
    public void largeMethod8() { /* ... */ }
    public void largeMethod9() { /* ... */ }
    public void largeMethod10() { /* ... */ }
    public void largeMethod11() { /* ... */ }
    public void largeMethod12() { /* ... */ }
    public void largeMethod13() { /* ... */ }
    public void largeMethod14() { /* ... */ }
    public void largeMethod15() { /* ... */ }
    public void largeMethod16() { /* ... */ }
    public void largeMethod17() { /* ... */ }
    public void largeMethod18() { /* ... */ }
    public void largeMethod19() { /* ... */ }
    public void largeMethod20() { /* ... */ }
    public void largeMethod21() { /* ... */ }
    public void largeMethod22() { /* ... */ }
    public void largeMethod23() { /* ... */ }
    public void largeMethod24() { /* ... */ }
    public void largeMethod25() { /* ... */ }
    public void largeMethod26() { /* ... */ }
    public void largeMethod27() { /* ... */ }
    public void largeMethod28() { /* ... */ }
    public void largeMethod29() { /* ... */ }
    public void largeMethod30() { /* ... */ }
    public void largeMethod31() { /* ... */ }
    public void largeMethod32() { /* ... */ }
    public void largeMethod33() { /* ... */ }
    public void largeMethod34() { /* ... */ }
    public void largeMethod35() { /* ... */ }
    public void largeMethod36() { /* ... */ }
    public void largeMethod37() { /* ... */ }
    public void largeMethod38() { /* ... */ }
    public void largeMethod39() { /* ... */ }
    public void largeMethod40() { /* ... */ }
    public void largeMethod41() { /* ... */ }
    public void largeMethod42() { /* ... */ }
    public void largeMethod43() { /* ... */ }
    public void largeMethod44() { /* ... */ }
    public void largeMethod45() { /* ... */ }
    public void largeMethod46() { /* ... */ }
    public void largeMethod47() { /* ... */ }
    public void largeMethod48() { /* ... */ }
    public void largeMethod49() { /* ... */ }
    public void largeMethod50() { /* ... */ }
    public void largeMethod51() { /* ... */ }
    public void largeMethod52() { /* ... */ }
    public void largeMethod53() { /* ... */ }
    public void largeMethod54() { /* ... */ }
    public void largeMethod55() { /* ... */ }
    public void largeMethod56() { /* ... */ }
    public void largeMethod57() { /* ... */ }
    public void largeMethod58() { /* ... */ }
    public void largeMethod59() { /* ... */ }
    public void largeMethod60() { /* ... */ }
    public void largeMethod61() { /* ... */ }
    public void largeMethod62() { /* ... */ }
    public void largeMethod63() { /* ... */ }
    public void largeMethod64() { /* ... */ }
    public void largeMethod65() { /* ... */ }
    public void largeMethod66() { /* ... */ }
    public void largeMethod67() { /* ... */ }
    public void largeMethod68() { /* ... */ }
    public void largeMethod69() { /* ... */ }
    public void largeMethod70() { /* ... */ }
    public void largeMethod71() { /* ... */ }
    public void largeMethod72() { /* ... */ }
    public void largeMethod73() { /* ... */ }
    public void largeMethod74() { /* ... */ }
    public void largeMethod75() { /* ... */ }
    public void largeMethod76() { /* ... */ }
    public void largeMethod77() { /* ... */ }
    public void largeMethod78() { /* ... */ }
    public void largeMethod79() { /* ... */ }
    public void largeMethod80() { /* ... */ }
    public void largeMethod81() { /* ... */ }
    public void largeMethod82() { /* ... */ }
    public void largeMethod83() { /* ... */ }
    public void largeMethod84() { /* ... */ }
    public void largeMethod85() { /* ... */ }
    public void largeMethod86() { /* ... */ }
    public void largeMethod87() { /* ... */ }
    public void largeMethod88() { /* ... */ }
    public void largeMethod89() { /* ... */ }
    public void largeMethod90() { /* ... */ }
    public void largeMethod91() { /* ... */ }
    public void largeMethod92() { /* ... */ }
    public void largeMethod93() { /* ... */ }
    public void largeMethod94() { /* ... */ }
    public void largeMethod95() { /* ... */ }
    public void largeMethod96() { /* ... */ }
    public void largeMethod97() { /* ... */ }
    public void largeMethod98() { /* ... */ }
    public void largeMethod99() { /* ... */ }
    public void largeMethod100() { /* ... */ }
}