package com.example.model;

import java.time.LocalDateTime;

/**
 * Customer domain model representing customers within the sample application.
 *
 * <p>This class defines basic fields such as {@code id}, {@code name},
 * {@code email}, optional {@code phone} number and the timestamp when
 * the customer joined the service. Providing getters and setters enables
 * integration with frameworks like MyBatis or Spring Data.</p>
 */
public class Customer {
    /**
     * Primary identifier of the customer.
     */
    private Long id;

    /**
     * Name of the customer.
     */
    private String name;

    /**
     * E-mail address of the customer.
     */
    private String email;

    /**
     * Optional phone number.
     */
    private String phone;

    /**
     * Timestamp when the customer registered or joined the service.
     */
    private LocalDateTime joinedAt;

    public Customer() {
    }

    public Customer(Long id, String name, String email, String phone, LocalDateTime joinedAt) {
        this.id = id;
        this.name = name;
        this.email = email;
        this.phone = phone;
        this.joinedAt = joinedAt;
    }

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

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public String getPhone() {
        return phone;
    }

    public void setPhone(String phone) {
        this.phone = phone;
    }

    public LocalDateTime getJoinedAt() {
        return joinedAt;
    }

    public void setJoinedAt(LocalDateTime joinedAt) {
        this.joinedAt = joinedAt;
    }
}