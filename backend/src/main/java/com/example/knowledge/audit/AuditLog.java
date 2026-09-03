package com.example.knowledge.audit;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import java.time.Instant;
import java.util.UUID;

/** Immutable audit record for security-relevant actions. */
@Entity
@Table(name = "audit_logs")
public class AuditLog {

    @Id
    private String id;

    @Column(name = "user_id", nullable = false)
    private String userId;

    @Column(nullable = false)
    private String action;

    @Column(name = "resource_id")
    private String resourceId;

    @Column(nullable = false)
    private String detail;

    @Column(name = "created_at", nullable = false)
    private Instant createdAt = Instant.now();

    protected AuditLog() {}

    public AuditLog(String userId, String action, String resourceId, String detail) {
        this.id = UUID.randomUUID().toString();
        this.userId = userId;
        this.action = action;
        this.resourceId = resourceId;
        this.detail = detail;
        this.createdAt = Instant.now();
    }

    public String getId() {
        return id;
    }

    public String getUserId() {
        return userId;
    }

    public String getAction() {
        return action;
    }

    public String getResourceId() {
        return resourceId;
    }

    public String getDetail() {
        return detail;
    }

    public Instant getCreatedAt() {
        return createdAt;
    }
}
