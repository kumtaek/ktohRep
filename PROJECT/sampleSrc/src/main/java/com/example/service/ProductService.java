package com.example.service;

import org.springframework.stereotype.Service;
import org.springframework.beans.factory.annotation.Autowired;
import java.util.List;
import java.util.Map;

@Service
public class ProductService {

    @Autowired
    private com.example.mapper.ProductMapper productMapper;

    public List<Object> getProductList() {
        return productMapper.selectAllProducts();
    }

    /*
     * 상품 세부정보 조회
     * 간단한 주석
     */
    public Object getProductDetails(String productId) {
        return productMapper.selectProductById(productId);
    }

    /**
     * @MethodName : searchProducts
     * @Description : 조건에 따라 상품을 검색합니다. 복잡한 WHERE 조건과 동적 SQL 사용
     * @Parameters : Map<String, Object> criteria - 검색 조건
     * @Return : List<Object> - 검색된 상품 목록
     */
    public List<Object> searchProducts(Map<String, Object> criteria) {
        return productMapper.searchProductsWithCriteria(criteria);
    }

    // 성능 이슈가 있을 수 있는 메서드
    public void processComplexBusiness(String input) {
        // 복잡한 중첩 조건문 - 복잡도 증가 요인
        if (input != null) {
            if (input.length() > 0) {
                if (input.contains("A")) {
                    if (input.startsWith("B")) {
                        for (int i = 0; i < input.length(); i++) {
                            for (int j = 0; j < input.length(); j++) {
                                // 이중 루프 - 성능 이슈 가능성
                                System.out.println(input.charAt(i) + "" + input.charAt(j));
                            }
                        }
                    }
                }
            }
        }
    }

    // 취약점 패턴 예제 - SQL Injection 가능성
    public List<Object> unsafeProductSearch(String category) {
        String sql = "SELECT * FROM products WHERE category = '" + category + "'";
        return productMapper.executeDynamicQuery(sql);
    }
}