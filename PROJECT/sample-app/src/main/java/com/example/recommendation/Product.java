package com.example.recommendation;

import java.util.ArrayList;
import java.util.List;

/**
 * Domain model representing a product in the recommendation engine.
 *
 * <p>Each product may have an arbitrary number of tags (keywords) and
 * an optional score computed by the recommendation algorithm. The score
 * is transient and not persisted in the database.</p>
 */
public class Product {
    private Long id;
    private String name;
    private List<String> tags = new ArrayList<>();
    private double score;

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public List<String> getTags() {
        return tags;
    }

    public void setTags(List<String> tags) {
        this.tags = tags;
    }

    public double getScore() {
        return score;
    }

    public void setScore(double score) {
        this.score = score;
    }
}