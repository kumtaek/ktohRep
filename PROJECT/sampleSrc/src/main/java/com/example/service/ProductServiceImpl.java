package com.example.service;

import com.example.mapper.ProductMapper;
import com.example.model.Product;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Map;

@Service
@Transactional
public class ProductServiceImpl implements ProductService {
    
    @Autowired
    private ProductMapper productMapper;
    
    @Override
    public List<Product> getProductsByCondition(Map<String, Object> params) {
        return productMapper.selectProductsByCondition(params);
    }
    
    @Override
    public List<Product> getProductsByAdvancedCondition(Map<String, Object> params) {
        return productMapper.selectProductsByAdvancedCondition(params);
    }
    
    @Override
    public List<Product> getProductsByCategory(String categoryId) {
        return productMapper.selectProductsByCategory(categoryId);
    }
    
    @Override
    public Product getProductById(String productId) {
        return productMapper.selectProductById(productId);
    }
    
    @Override
    public int updateProductStock(String productId, int quantity) {
        return productMapper.updateProductStock(productId, quantity);
    }
    
    @Override
    public int updateProductDynamic(Product product) {
        return productMapper.updateProductDynamic(product);
    }
    
    @Override
    public int deleteProductsByCondition(Map<String, Object> params) {
        return productMapper.deleteProductsByCondition(params);
    }
}
