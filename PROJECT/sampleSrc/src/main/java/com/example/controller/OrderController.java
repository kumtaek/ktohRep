package com.example.controller;

import org.springframework.web.bind.annotation.*;
import org.springframework.beans.factory.annotation.Autowired;
import com.example.order.OrderService;
import com.example.product.ProductService;
import com.example.user.UserService;
import java.util.List;
import java.util.Map;

/**
 * 주문 관리 컨트롤러
 * 주문 생성, 조회, 수정, 삭제 및 주문 상태 관리
 */
@RestController
@RequestMapping("/api/orders")
public class OrderController {
    
    @Autowired
    private OrderService orderService;
    
    @Autowired
    private ProductService productService;
    
    @Autowired
    private UserService userService;
    
    /**
     * 새로운 주문 생성
     */
    @PostMapping
    public ResponseEntity<Order> createOrder(@RequestBody OrderRequest request) {
        try {
            // 사용자 검증
            User user = userService.getUserById(request.getUserId());
            if (user == null) {
                return ResponseEntity.badRequest().build();
            }
            
            // 상품 검증 및 재고 확인
            for (OrderItem item : request.getItems()) {
                Product product = productService.getProductById(item.getProductId());
                if (product == null || product.getStock() < item.getQuantity()) {
                    return ResponseEntity.badRequest().build();
                }
            }
            
            // 주문 생성
            Order order = orderService.createOrder(request);
            
            // 재고 업데이트
            updateInventory(request.getItems());
            
            // 주문 확인 이메일 발송
            notificationService.sendOrderConfirmation(user.getEmail(), order);
            
            return ResponseEntity.ok(order);
            
        } catch (Exception e) {
            logger.error("주문 생성 실패: " + e.getMessage(), e);
            return ResponseEntity.internalServerError().build();
        }
    }
    
    /**
     * 주문 목록 조회
     */
    @GetMapping
    public ResponseEntity<List<Order>> getOrders(
            @RequestParam(required = false) String status,
            @RequestParam(required = false) Long userId,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {
        
        try {
            List<Order> orders;
            
            if (userId != null) {
                orders = orderService.getOrdersByUserId(userId, status, page, size);
            } else {
                orders = orderService.getAllOrders(status, page, size);
            }
            
            return ResponseEntity.ok(orders);
            
        } catch (Exception e) {
            logger.error("주문 목록 조회 실패: " + e.getMessage(), e);
            return ResponseEntity.internalServerError().build();
        }
    }
    
    /**
     * 특정 주문 상세 조회
     */
    @GetMapping("/{orderId}")
    public ResponseEntity<OrderDetail> getOrderDetail(@PathVariable Long orderId) {
        try {
            Order order = orderService.getOrderById(orderId);
            if (order == null) {
                return ResponseEntity.notFound().build();
            }
            
            // 주문 아이템 상세 정보 로드
            List<OrderItemDetail> items = orderService.getOrderItems(orderId);
            
            // 배송 정보 로드
            ShippingInfo shipping = shippingService.getShippingInfo(orderId);
            
            OrderDetail detail = new OrderDetail(order, items, shipping);
            return ResponseEntity.ok(detail);
            
        } catch (Exception e) {
            logger.error("주문 상세 조회 실패: " + e.getMessage(), e);
            return ResponseEntity.internalServerError().build();
        }
    }
    
    /**
     * 주문 상태 업데이트
     */
    @PutMapping("/{orderId}/status")
    public ResponseEntity<Order> updateOrderStatus(
            @PathVariable Long orderId,
            @RequestBody Map<String, String> statusUpdate) {
        
        try {
            String newStatus = statusUpdate.get("status");
            Order updatedOrder = orderService.updateOrderStatus(orderId, newStatus);
            
            if (updatedOrder == null) {
                return ResponseEntity.notFound().build();
            }
            
            // 상태 변경 알림 발송
            if ("SHIPPED".equals(newStatus)) {
                User user = userService.getUserById(updatedOrder.getUserId());
                notificationService.sendShippingNotification(user.getEmail(), updatedOrder);
            }
            
            return ResponseEntity.ok(updatedOrder);
            
        } catch (Exception e) {
            logger.error("주문 상태 업데이트 실패: " + e.getMessage(), e);
            return ResponseEntity.internalServerError().build();
        }
    }
    
    /**
     * 주문 취소
     */
    @DeleteMapping("/{orderId}")
    public ResponseEntity<Void> cancelOrder(@PathVariable Long orderId) {
        try {
            Order order = orderService.getOrderById(orderId);
            if (order == null) {
                return ResponseEntity.notFound().build();
            }
            
            // 취소 가능 상태 확인
            if (!orderService.isCancellable(order.getStatus())) {
                return ResponseEntity.badRequest().build();
            }
            
            // 재고 복원
            List<OrderItem> items = orderService.getOrderItems(orderId);
            restoreInventory(items);
            
            // 주문 취소 처리
            orderService.cancelOrder(orderId);
            
            // 취소 알림 발송
            User user = userService.getUserById(order.getUserId());
            notificationService.sendCancellationNotification(user.getEmail(), order);
            
            return ResponseEntity.ok().build();
            
        } catch (Exception e) {
            logger.error("주문 취소 실패: " + e.getMessage(), e);
            return ResponseEntity.internalServerError().build();
        }
    }
    
    /**
     * 재고 업데이트
     */
    private void updateInventory(List<OrderItem> items) {
        for (OrderItem item : items) {
            productService.decreaseStock(item.getProductId(), item.getQuantity());
        }
    }
    
    /**
     * 재고 복원
     */
    private void restoreInventory(List<OrderItem> items) {
        for (OrderItem item : items) {
            productService.increaseStock(item.getProductId(), item.getQuantity());
        }
    }
    
    /**
     * 주문 통계 조회
     */
    @GetMapping("/statistics")
    public ResponseEntity<OrderStatistics> getOrderStatistics(
            @RequestParam(required = false) String startDate,
            @RequestParam(required = false) String endDate) {
        
        try {
            OrderStatistics stats = orderService.getOrderStatistics(startDate, endDate);
            return ResponseEntity.ok(stats);
            
        } catch (Exception e) {
            logger.error("주문 통계 조회 실패: " + e.getMessage(), e);
            return ResponseEntity.internalServerError().build();
        }
    }
}