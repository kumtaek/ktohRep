package com.example.recommendation;

import org.apache.ibatis.annotations.Param;
import java.util.List;
import java.util.Map;

/**
 * MyBatis mapper interface for product queries used by the recommendation service.
 */
public interface ProductMapper {

    /**
     * Find products that match the provided set of tags. The MyBatis XML for
     * this query uses dynamic SQL with nested &lt;foreach&gt; loops to build a
     * flexible query that matches any number of tags.
     *
     * @param params map containing a key "tags" with a list of tag strings
     * @return list of products satisfying the tag criteria
     */
    List<Product> findByTags(@Param("params") Map<String, Object> params);
}