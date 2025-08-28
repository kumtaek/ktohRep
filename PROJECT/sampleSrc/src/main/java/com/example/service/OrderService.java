package com.example.service;

import org.springframework.stereotype.Service;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.transaction.annotation.Transactional;
import java.math.BigDecimal;
import java.util.List;

@Service
@Transactional
public class OrderService {

    @Autowired
    private com.example.mapper.OrderMapper orderMapper;

    /**
     * @MethodName : calculateOrderTotal
     * @Description : 주문 총액을 계산합니다. 할인과 세금을 포함한 최종 금액을 반환합니다.
     * @Parameters : String orderId - 주문 ID, BigDecimal discountRate - 할인율
     * @Return : BigDecimal - 계산된 총액
     * @Throws : IllegalArgumentException - 유효하지 않은 주문 ID인 경우
     */
    public BigDecimal calculateOrderTotal(String orderId, BigDecimal discountRate) {
        Object order = orderMapper.selectOrderById(orderId);
        if (order == null) {
            throw new IllegalArgumentException("주문을 찾을 수 없습니다: " + orderId);
        }
        
        BigDecimal baseAmount = orderMapper.calculateOrderAmount(orderId);
        BigDecimal discount = baseAmount.multiply(discountRate);
        BigDecimal subtotal = baseAmount.subtract(discount);
        BigDecimal tax = subtotal.multiply(new BigDecimal("0.10"));
        
        return subtotal.add(tax);
    }

    /**
     * 주문 상태별 조회 - 복합 조건 사용
     */
    public List<Object> getOrdersByStatus(String status) {
        return orderMapper.selectOrdersByStatus(status);
    }

    /**
     * 복잡한 주문 보고서 생성 - 다중 테이블 조인
     */
    public Object generateOrderReport(String startDate, String endDate) {
        return orderMapper.getComplexOrderReport(startDate, endDate);
    }

    // 반복적인 대용량 데이터 처리 시뮬레이션
    public void largeOrderMethod1() {
        for (int i = 0; i < 1000; i++) {
            System.out.println("대용량 주문 처리 " + i);
        }
    }

    public void largeOrderMethod2() {
        for (int i = 0; i < 1000; i++) {
            System.out.println("대용량 주문 처리 " + i);
        }
    }

    public void largeOrderMethod3() {
        for (int i = 0; i < 1000; i++) {
            System.out.println("대용량 주문 처리 " + i);
        }
    }
}