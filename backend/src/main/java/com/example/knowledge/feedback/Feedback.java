package com.example.knowledge.feedback;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "feedback")
public class Feedback {

    @Id
    private String id;

    @Column(name = "message_id", nullable = false)
    private String messageId;

    @Column(name = "user_id", nullable = false)
    private String userId;

    /** -1 (thumbs down) or +1 (thumbs up). */
    @Column(nullable = false)
    private int rating;

    @Column
    private String comment;

    @Column(name = "created_at", nullable = false)
    private Instant createdAt = Instant.now();

    protected Feedback() {}

    public Feedback(String messageId, String userId, int rating, String comment) {
        this.id = UUID.randomUUID().toString();
        this.messageId = messageId;
        this.userId = userId;
        this.rating = rating;
        this.comment = comment;
        this.createdAt = Instant.now();
    }

    public String getId() {
        return id;
    }

    public String getMessageId() {
        return messageId;
    }

    public String getUserId() {
        return userId;
    }

    public int getRating() {
        return rating;
    }

    public String getComment() {
        return comment;
    }

    public Instant getCreatedAt() {
        return createdAt;
    }
}
