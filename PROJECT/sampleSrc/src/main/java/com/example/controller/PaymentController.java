package com.example.controller;

import org.springframework.web.bind.annotation.*;
import org.springframework.beans.factory.annotation.Autowired;
import com.example.payment.PaymentService;
import com.example.order.OrderService;
import com.example.notification.NotificationService;

/**
 * 결제 처리 컨트롤러
 * 결제 요청, 확인, 환불 처리
 */
@RestController
@RequestMapping("/api/payments")
public class PaymentController {
    
    @Autowired
    private PaymentService paymentService;
    
    @Autowired
    private OrderService orderService;
    
    @Autowired
    private NotificationService notificationService;
    
    /**
     * 결제 요청 처리
     */
    @PostMapping("/process")
    public ResponseEntity<PaymentResult> processPayment(@RequestBody PaymentRequest request) {
        try {
            // 주문 유효성 검증
            Order order = orderService.validateOrderForPayment(request.getOrderId());
            if (order == null) {
                return ResponseEntity.badRequest()
                    .body(new PaymentResult("FAILED", "잘못된 주문입니다"));
            }
            
            // 결제 금액 검증
            if (!validatePaymentAmount(order, request)) {
                return ResponseEntity.badRequest()
                    .body(new PaymentResult("FAILED", "결제 금액이 일치하지 않습니다"));
            }
            
            // 결제 처리
            PaymentResult result = paymentService.processPayment(request);
            
            if ("SUCCESS".equals(result.getStatus())) {
                // 주문 상태 업데이트
                orderService.updateOrderStatus(request.getOrderId(), "PAID");
                
                // 결제 완료 알림
                User user = orderService.getOrderOwner(request.getOrderId());
                notificationService.sendPaymentConfirmation(user.getEmail(), result);
                
                // 재고 확정 처리
                inventoryService.confirmStockReservation(request.getOrderId());
            }
            
            return ResponseEntity.ok(result);
            
        } catch (PaymentException e) {
            logger.error("결제 처리 실패: " + e.getMessage(), e);
            return ResponseEntity.badRequest()
                .body(new PaymentResult("FAILED", e.getMessage()));
                
        } catch (Exception e) {
            logger.error("결제 시스템 오류: " + e.getMessage(), e);
            return ResponseEntity.internalServerError()
                .body(new PaymentResult("ERROR", "시스템 오류가 발생했습니다"));
        }
    }
    
    /**
     * 결제 상태 조회
     */
    @GetMapping("/{paymentId}/status")
    public ResponseEntity<PaymentStatus> getPaymentStatus(@PathVariable String paymentId) {
        try {
            PaymentStatus status = paymentService.getPaymentStatus(paymentId);
            
            if (status == null) {
                return ResponseEntity.notFound().build();
            }
            
            return ResponseEntity.ok(status);
            
        } catch (Exception e) {
            logger.error("결제 상태 조회 실패: " + e.getMessage(), e);
            return ResponseEntity.internalServerError().build();
        }
    }
    
    /**
     * 환불 처리
     */
    @PostMapping("/{paymentId}/refund")
    public ResponseEntity<RefundResult> processRefund(
            @PathVariable String paymentId,
            @RequestBody RefundRequest request) {
        
        try {
            // 결제 정보 조회
            Payment payment = paymentService.getPayment(paymentId);
            if (payment == null) {
                return ResponseEntity.notFound().build();
            }
            
            // 환불 가능 여부 확인
            if (!paymentService.isRefundable(payment)) {
                return ResponseEntity.badRequest()
                    .body(new RefundResult("FAILED", "환불이 불가능한 결제입니다"));
            }
            
            // 환불 처리
            RefundResult result = paymentService.processRefund(paymentId, request);
            
            if ("SUCCESS".equals(result.getStatus())) {
                // 주문 상태 업데이트
                orderService.updateOrderStatus(payment.getOrderId(), "REFUNDED");
                
                // 재고 복원
                List<OrderItem> items = orderService.getOrderItems(payment.getOrderId());
                restoreInventory(items);
                
                // 환불 완료 알림
                User user = orderService.getOrderOwner(payment.getOrderId());
                notificationService.sendRefundNotification(user.getEmail(), result);
            }
            
            return ResponseEntity.ok(result);
            
        } catch (Exception e) {
            logger.error("환불 처리 실패: " + e.getMessage(), e);
            return ResponseEntity.internalServerError()
                .body(new RefundResult("ERROR", "환불 처리 중 오류가 발생했습니다"));
        }
    }
    
    /**
     * 결제 금액 검증
     */
    private boolean validatePaymentAmount(Order order, PaymentRequest request) {
        // 주문 총액 계산
        BigDecimal orderTotal = orderService.calculateOrderTotal(order.getOrderId());
        
        // 할인 적용
        BigDecimal discountAmount = discountService.calculateDiscount(order);
        BigDecimal finalAmount = orderTotal.subtract(discountAmount);
        
        // 요청된 결제 금액과 비교
        return finalAmount.compareTo(request.getAmount()) == 0;
    }
    
    /**
     * 부분 환불 처리
     */
    @PostMapping("/{paymentId}/partial-refund")
    public ResponseEntity<RefundResult> processPartialRefund(
            @PathVariable String paymentId,
            @RequestBody PartialRefundRequest request) {
        
        try {
            // 결제 정보 및 환불 이력 조회
            Payment payment = paymentService.getPayment(paymentId);
            List<Refund> existingRefunds = paymentService.getRefundHistory(paymentId);
            
            // 환불 가능 금액 계산
            BigDecimal totalRefunded = existingRefunds.stream()
                .map(Refund::getAmount)
                .reduce(BigDecimal.ZERO, BigDecimal::add);
                
            BigDecimal remainingAmount = payment.getAmount().subtract(totalRefunded);
            
            if (request.getAmount().compareTo(remainingAmount) > 0) {
                return ResponseEntity.badRequest()
                    .body(new RefundResult("FAILED", "환불 가능 금액을 초과했습니다"));
            }
            
            // 부분 환불 처리
            RefundResult result = paymentService.processPartialRefund(paymentId, request);
            
            if ("SUCCESS".equals(result.getStatus())) {
                // 부분 환불 알림
                User user = orderService.getOrderOwner(payment.getOrderId());
                notificationService.sendPartialRefundNotification(user.getEmail(), result);
            }
            
            return ResponseEntity.ok(result);
            
        } catch (Exception e) {
            logger.error("부분 환불 처리 실패: " + e.getMessage(), e);
            return ResponseEntity.internalServerError().build();
        }
    }
}