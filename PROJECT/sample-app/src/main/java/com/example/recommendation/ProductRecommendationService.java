package com.example.recommendation;

import org.springframework.stereotype.Service;
import org.springframework.beans.factory.annotation.Autowired;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;

/**
 * Service that recommends products based on a user's tags. It demonstrates
 * dynamic querying via MyBatis as well as post‑processing using a Jaccard
 * similarity measure to rank results.
 */
@Service
public class ProductRecommendationService {

    private final ProductMapper productMapper;

    @Autowired
    public ProductRecommendationService(ProductMapper productMapper) {
        this.productMapper = productMapper;
    }

    /**
     * Recommend products for a given set of user tags. The underlying mapper
     * performs a dynamic SQL query to retrieve candidates that share at least
     * one tag with the user. Results are then scored using Jaccard similarity
     * between the user's tags and each product's tags.
     *
     * @param userTags list of tags representing the user's interests
     * @return ranked list of products, highest score first
     */
    public List<Product> recommendByUserTags(List<String> userTags) {
        if (userTags == null || userTags.isEmpty()) {
            return Collections.emptyList();
        }
        Map<String, Object> params = new HashMap<>();
        params.put("tags", userTags);
        List<Product> candidates = productMapper.findByTags(params);
        Set<String> userSet = new HashSet<>(userTags);
        // Compute Jaccard similarity and assign scores
        for (Product p : candidates) {
            Set<String> productTags = new HashSet<>(p.getTags());
            Set<String> intersection = new HashSet<>(userSet);
            intersection.retainAll(productTags);
            Set<String> union = new HashSet<>(userSet);
            union.addAll(productTags);
            double score = union.isEmpty() ? 0.0 : (double) intersection.size() / union.size();
            p.setScore(score);
        }
        // Sort descending by score
        return candidates.stream()
                .sorted((a, b) -> Double.compare(b.getScore(), a.getScore()))
                .collect(Collectors.toList());
    }
}