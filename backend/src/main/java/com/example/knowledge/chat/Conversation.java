package com.example.knowledge.chat;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "conversations")
public class Conversation {

    @Id
    private String id;

    @Column(name = "user_id", nullable = false)
    private String userId;

    @Column(nullable = false)
    private String title;

    @Column(name = "created_at", nullable = false)
    private Instant createdAt = Instant.now();

    protected Conversation() {}

    public Conversation(String userId, String title) {
        this.id = UUID.randomUUID().toString();
        this.userId = userId;
        this.title = title;
        this.createdAt = Instant.now();
    }

    public String getId() {
        return id;
    }

    public String getUserId() {
        return userId;
    }

    public String getTitle() {
        return title;
    }

    public Instant getCreatedAt() {
        return createdAt;
    }
}
